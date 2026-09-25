"""
SSH Client — manages SSH connections to TwinNet VMs.

Uses paramiko under the hood.
Connections are cached per host so we don't re-connect on every call.
Fails gracefully — if a VM is offline, returns None instead of crashing.
"""

import logging
import socket
from typing import Optional

import paramiko

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# VM registry — maps short names to IPs
# ─────────────────────────────────────────────────────────────────────────────
VM_HOSTS = {
    "vm1": settings.DT_VM1_HOST,
    "vm2": settings.DT_VM2_HOST,
}

SSH_TIMEOUT = 8   # seconds


class SSHClient:
    """Thin wrapper around paramiko for running commands on VMs."""

    def __init__(self, host: str, port: int = 22, username: str = "ubuntu", password: str = "ubuntu123") -> None:
        self.host     = host
        self.port     = port
        self.username = username
        self.password = password
        self._client: Optional[paramiko.SSHClient] = None

    # ─────────────────────────────────────────────────────────────────────────
    # Connection
    # ─────────────────────────────────────────────────────────────────────────

    def connect(self) -> bool:
        """Establish SSH connection. Returns True on success, False if unreachable."""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=SSH_TIMEOUT,
                look_for_keys=False,
                allow_agent=False,
            )
            self._client = client
            logger.info("SSH connected → %s@%s", self.username, self.host)
            return True
        except (socket.timeout, paramiko.AuthenticationException,
                paramiko.SSHException, OSError) as e:
            logger.warning("SSH connect failed for %s: %s", self.host, e)
            self._client = None
            return False

    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None and self._client.get_transport() is not None

    # ─────────────────────────────────────────────────────────────────────────
    # Command execution
    # ─────────────────────────────────────────────────────────────────────────

    def exec(self, command: str, timeout: int = 15) -> dict:
        """
        Run a shell command on the remote VM.

        Returns:
            { "stdout": str, "stderr": str, "exit_code": int, "ok": bool }
        """
        if not self.is_connected:
            if not self.connect():
                return {"stdout": "", "stderr": "SSH not connected", "exit_code": -1, "ok": False}

        try:
            _, stdout, stderr = self._client.exec_command(command, timeout=timeout)
            out  = stdout.read().decode("utf-8", errors="replace").strip()
            err  = stderr.read().decode("utf-8", errors="replace").strip()
            code = stdout.channel.recv_exit_status()
            return {"stdout": out, "stderr": err, "exit_code": code, "ok": code == 0}
        except Exception as e:
            logger.error("SSH exec error on %s: %s", self.host, e)
            self._client = None  # mark as disconnected
            return {"stdout": "", "stderr": str(e), "exit_code": -1, "ok": False}

    def exec_sudo(self, command: str, timeout: int = 15) -> dict:
        """Run a command with sudo (password-based)."""
        return self.exec(
            f"echo '{self.password}' | sudo -S {command}",
            timeout=timeout,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Reachability check
    # ─────────────────────────────────────────────────────────────────────────

    def ping(self) -> bool:
        """Quick TCP check to see if VM is reachable (no SSH needed)."""
        try:
            with socket.create_connection((self.host, self.port), timeout=3):
                return True
        except OSError:
            return False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()


# ─────────────────────────────────────────────────────────────────────────────
# Factory helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_vm_client(vm_name: str, password: str = "ubuntu123") -> SSHClient:
    """
    Get an SSH client for a named VM (vm1 or vm2).
    Uses password authentication (set up during VM installation).
    """
    host = VM_HOSTS.get(vm_name.lower())
    if not host:
        raise ValueError(f"Unknown VM name: {vm_name!r}. Use 'vm1' or 'vm2'.")
    return SSHClient(host=host, port=22, username=settings.DT_SSH_USER, password=password)

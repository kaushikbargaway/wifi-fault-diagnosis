"""Centralised application configuration loaded from environment variables."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # -----------------------------------------------------------------------
    # General
    # -----------------------------------------------------------------------
    PROJECT_NAME: str = "WiFi Fault Diagnosis API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # -----------------------------------------------------------------------
    # Database
    # -----------------------------------------------------------------------
    DATABASE_URL: str = "sqlite:///./wifi_fault.db"  # override via .env

    # -----------------------------------------------------------------------
    # Machine Learning
    # -----------------------------------------------------------------------
    MODEL_PATH: str = "models/random_forest.pkl"
    # Ordered list of feature names the model expects
    ML_FEATURES: List[str] = [
        "rssi_dbm",
        "latency_ms",
        "packet_loss_percent",
        "internet_reachable",
        "dns_available",
        "ethernet_connected",
        "temperature_c",
        "network_load",
    ]
    FAULT_LABELS: List[str] = [
        "normal",
        "weak_wifi_signal",
        "high_latency",
        "packet_loss",
        "dns_failure",
        "internet_connectivity_failure",
        "ethernet_problem",
        "router_overheating",
        "network_congestion",
    ]

    # -----------------------------------------------------------------------
    # Digital Twin
    # -----------------------------------------------------------------------
    DT_VM1_HOST: str = "192.168.56.101"
    DT_VM1_PORT: int = 22
    DT_VM2_HOST: str = "192.168.56.102"
    DT_VM2_PORT: int = 22
    DT_SSH_USER: str = "ubuntu"
    DT_SSH_KEY_PATH: str = "~/.ssh/id_rsa"

    # -----------------------------------------------------------------------
    # RAG / LLM
    # -----------------------------------------------------------------------
    LLM_PROVIDER: str = "openai"          # openai | ollama | huggingface
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    VECTORSTORE_PATH: str = "rag/vectorstore"

    # -----------------------------------------------------------------------
    # ESP32 / Telemetry
    # -----------------------------------------------------------------------
    USE_SIMULATED_TELEMETRY: bool = True   # set False when real hardware is used
    TELEMETRY_SIMULATION_INTERVAL_S: int = 5


settings = Settings()

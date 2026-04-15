package config

import (
	"net/url"
	"os"
	"strings"

	"github.com/joho/godotenv"
)

type Config struct {
	AppName           string
	Port              string
	DatabaseURL       string
	LegacyDatabaseURL string
	GinMode           string
	JWTSecret         string
}

func Load() Config {
	loadEnvFiles()

	cfg := Config{
		AppName:           getEnv("APP_NAME", "hcs-cms-go"),
		Port:              getEnv("PORT", "8080"),
		DatabaseURL:       os.Getenv("DATABASE_URL"),
		LegacyDatabaseURL: resolveLegacyDatabaseURL(),
		GinMode:           getEnv("GIN_MODE", "debug"),
		JWTSecret:         getEnv("JWT_SECRET", "change-me"),
	}

	if cfg.GinMode != "" {
		os.Setenv("GIN_MODE", cfg.GinMode)
	}

	return cfg
}

func loadEnvFiles() {
	// Try common working directories without overriding already exported env vars.
	for _, envPath := range []string{".env", "../.env", "../../.env"} {
		_ = godotenv.Load(envPath)
	}
}

func getEnv(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}

func resolveLegacyDatabaseURL() string {
	if value := strings.TrimSpace(os.Getenv("LEGACY_DATABASE_URL")); value != "" {
		return value
	}

	name := strings.TrimSpace(os.Getenv("CIS_LEGACY_DB_NAME"))
	if name == "" {
		return ""
	}

	user := strings.TrimSpace(os.Getenv("CIS_LEGACY_DB_USER"))
	password := os.Getenv("CIS_LEGACY_DB_PASSWORD")
	host := getEnv("CIS_LEGACY_DB_HOST", "localhost")
	port := getEnv("CIS_LEGACY_DB_PORT", "5432")

	legacyURL := &url.URL{
		Scheme: "postgresql",
		Host:   host + ":" + port,
		Path:   "/" + name,
	}
	if user != "" {
		legacyURL.User = url.UserPassword(user, password)
	}

	return legacyURL.String()
}

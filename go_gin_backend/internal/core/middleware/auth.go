package middleware

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"

	coreaudit "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/audit"
	coreauth "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/auth"
)

const claimsContextKey = "auth_claims"

func OptionalAuth(jwtSecret string) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := strings.TrimSpace(c.GetHeader("Authorization"))
		if authHeader == "" {
			c.Next()
			return
		}

		tokenString, ok := extractBearerToken(authHeader)
		if !ok {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"detail": "invalid authorization header"})
			return
		}

		claims, err := coreauth.ParseToken(tokenString, jwtSecret)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"detail": "invalid token"})
			return
		}

		ctx := coreaudit.WithUserID(c.Request.Context(), claims.UserID)
		c.Request = c.Request.WithContext(ctx)
		c.Set(claimsContextKey, claims)

		c.Next()
	}
}

func AuthRequired(jwtSecret string) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := strings.TrimSpace(c.GetHeader("Authorization"))
		tokenString, ok := extractBearerToken(authHeader)
		if !ok {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"detail": "authentication credentials were not provided"})
			return
		}

		claims, err := coreauth.ParseToken(tokenString, jwtSecret)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"detail": "invalid token"})
			return
		}

		ctx := coreaudit.WithUserID(c.Request.Context(), claims.UserID)
		c.Request = c.Request.WithContext(ctx)
		c.Set(claimsContextKey, claims)
		c.Next()
	}
}

func extractBearerToken(header string) (string, bool) {
	parts := strings.Fields(header)
	if len(parts) != 2 || !strings.EqualFold(parts[0], "Bearer") {
		return "", false
	}
	if strings.TrimSpace(parts[1]) == "" {
		return "", false
	}
	return parts[1], true
}

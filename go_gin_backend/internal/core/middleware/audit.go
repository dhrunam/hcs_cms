package middleware

import "github.com/gin-gonic/gin"

func AuditContext() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()
	}
}

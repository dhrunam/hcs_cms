package handler

import (
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/accounts/service"
	coreauth "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/auth"
	coreerrors "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/errors"
)

type Handler struct {
	service *service.Service
}

func New(svc *service.Service) *Handler {
	return &Handler{service: svc}
}

func (h *Handler) Me(c *gin.Context) {
	claimsVal, ok := c.Get("auth_claims")
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"detail": "authentication credentials were not provided"})
		return
	}

	claims, ok := claimsVal.(*coreauth.Claims)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"detail": "invalid token"})
		return
	}

	user, err := h.service.Me(c.Request.Context(), claims.UserID)
	if err != nil {
		h.writeError(c, err)
		return
	}

	c.JSON(http.StatusOK, user)
}

func (h *Handler) Logout(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"detail": "Logged out successfully."})
}

func (h *Handler) TokenVerify(c *gin.Context) {
	var body struct {
		Token string `json:"token"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"detail": "invalid request body"})
		return
	}

	_, err := coreauth.ParseToken(body.Token, c.GetString("jwt_secret"))
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"detail": "Token is invalid or expired"})
		return
	}

	c.JSON(http.StatusOK, gin.H{})
}

func (h *Handler) NotImplemented(c *gin.Context) {
	c.JSON(http.StatusNotImplemented, gin.H{
		"detail": "This endpoint is not implemented in Go backend yet. Use DRF backend for this operation.",
	})
}

func (h *Handler) writeError(c *gin.Context, err error) {
	var httpErr coreerrors.HTTPError
	if ok := errors.As(err, &httpErr); ok {
		c.JSON(httpErr.Status, gin.H{"detail": httpErr.Message})
		return
	}
	c.JSON(http.StatusInternalServerError, gin.H{"detail": err.Error()})
}

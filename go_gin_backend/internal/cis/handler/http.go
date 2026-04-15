package handler

import (
	"errors"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"

	coreerrors "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/errors"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/service"
)

type Handler struct {
	service *service.Service
}

func New(svc *service.Service) *Handler {
	return &Handler{service: svc}
}

func (h *Handler) MigrateStates(c *gin.Context) {
	limit := h.parseLimit(c)

	summary, err := h.service.MigrateStates(c.Request.Context(), limit)
	if err != nil {
		h.writeError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"detail":  "states migrated successfully",
		"created": summary.Created,
		"updated": summary.Updated,
		"skipped": summary.Skipped,
	})
}

func (h *Handler) MigrateCaseTypes(c *gin.Context) {
	limit := h.parseLimit(c)

	summary, err := h.service.MigrateCaseTypes(c.Request.Context(), limit)
	if err != nil {
		h.writeError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"detail":  "case types migrated successfully",
		"created": summary.Created,
		"updated": summary.Updated,
		"skipped": summary.Skipped,
	})
}

func (h *Handler) MigrateActs(c *gin.Context) {
	limit := h.parseLimit(c)

	summary, err := h.service.MigrateActs(c.Request.Context(), limit)
	if err != nil {
		h.writeError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"detail":  "acts migrated successfully",
		"created": summary.Created,
		"updated": summary.Updated,
		"skipped": summary.Skipped,
	})
}

func (h *Handler) MigrateAll(c *gin.Context) {
	limit := h.parseLimit(c)

	summaries := []gin.H{}

	statesSummary, err := h.service.MigrateStates(c.Request.Context(), limit)
	if err != nil {
		h.writeError(c, err)
		return
	}
	summaries = append(summaries, gin.H{
		"entity":  "states",
		"created": statesSummary.Created,
		"updated": statesSummary.Updated,
		"skipped": statesSummary.Skipped,
	})

	caseTypesSummary, err := h.service.MigrateCaseTypes(c.Request.Context(), limit)
	if err != nil {
		h.writeError(c, err)
		return
	}
	summaries = append(summaries, gin.H{
		"entity":  "case_types",
		"created": caseTypesSummary.Created,
		"updated": caseTypesSummary.Updated,
		"skipped": caseTypesSummary.Skipped,
	})

	actsSummary, err := h.service.MigrateActs(c.Request.Context(), limit)
	if err != nil {
		h.writeError(c, err)
		return
	}
	summaries = append(summaries, gin.H{
		"entity":  "acts",
		"created": actsSummary.Created,
		"updated": actsSummary.Updated,
		"skipped": actsSummary.Skipped,
	})

	c.JSON(http.StatusOK, gin.H{
		"detail":    "all migrations completed successfully",
		"summaries": summaries,
	})
}

func (h *Handler) parseLimit(c *gin.Context) *int {
	limitStr := c.DefaultQuery("limit", "")
	if limitStr == "" {
		return nil
	}

	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit < 1 {
		return nil
	}

	return &limit
}

func (h *Handler) writeError(c *gin.Context, err error) {
	var httpErr coreerrors.HTTPError
	if ok := asHTTPError(err, &httpErr); ok {
		c.JSON(httpErr.Status, gin.H{"detail": httpErr.Message})
		return
	}
	c.JSON(http.StatusInternalServerError, gin.H{"detail": err.Error()})
}

func asHTTPError(err error, target *coreerrors.HTTPError) bool {
	return errors.As(err, target)
}

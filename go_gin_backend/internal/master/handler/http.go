package handler

import (
	"errors"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"

	coreerrors "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/errors"
	coreresponse "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/response"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/service"
)

type Handler struct {
	service *service.Service
}

func New(svc *service.Service) *Handler {
	return &Handler{service: svc}
}

func (h *Handler) ListCaseTypes(c *gin.Context) {
	data, err := h.service.ListCaseTypes(c.Request.Context())
	if err != nil {
		h.writeError(c, err)
		return
	}

	c.JSON(http.StatusOK, data)
}

func (h *Handler) ListStates(c *gin.Context) {
	data, err := h.service.ListStates(c.Request.Context())
	if err != nil {
		h.writeError(c, err)
		return
	}

	c.JSON(http.StatusOK, data)
}

func (h *Handler) ListDistricts(c *gin.Context) {
	data, err := h.service.ListDistricts(c.Request.Context(), c.Query("state_id"))
	if err != nil {
		h.writeError(c, err)
		return
	}

	c.JSON(http.StatusOK, data)
}

func (h *Handler) ListActs(c *gin.Context) {
	data, err := h.service.ListActs(c.Request.Context())
	if err != nil {
		h.writeError(c, err)
		return
	}

	c.JSON(http.StatusOK, data)
}

func (h *Handler) ListCourts(c *gin.Context) {
	pageStr := c.DefaultQuery("page", "1")
	pageSizeStr := c.DefaultQuery("page_size", "20")

	page, err := strconv.Atoi(pageStr)
	if err != nil || page < 1 {
		page = 1
	}

	pageSize, err := strconv.Atoi(pageSizeStr)
	if err != nil || pageSize < 1 {
		pageSize = 20
	}

	data, total, err := h.service.ListCourtsWithPagination(c.Request.Context(), page, pageSize)
	if err != nil {
		h.writeError(c, err)
		return
	}

	response := coreresponse.NewPaginatedResponse(total, page, pageSize, data)
	c.JSON(http.StatusOK, response)
}

func (h *Handler) ListOrgTypes(c *gin.Context) {
	data, err := h.service.ListOrgTypes(c.Request.Context())
	if err != nil {
		h.writeError(c, err)
		return
	}

	c.JSON(http.StatusOK, data)
}

func (h *Handler) ListOrgNames(c *gin.Context) {
	data, err := h.service.ListOrgNames(c.Request.Context())
	if err != nil {
		h.writeError(c, err)
		return
	}

	c.JSON(http.StatusOK, data)
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

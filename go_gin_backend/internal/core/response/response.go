package response

import "github.com/gin-gonic/gin"

type envelope struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

type PaginatedResponse struct {
	Count    int64       `json:"count"`
	Next     interface{} `json:"next"`
	Previous interface{} `json:"previous"`
	Results  interface{} `json:"results"`
}

func Success(c *gin.Context, status int, data interface{}) {
	c.JSON(status, envelope{Success: true, Data: data})
}

func Error(c *gin.Context, status int, message string) {
	c.JSON(status, envelope{Success: false, Error: message})
}

func NewPaginatedResponse(count int64, page, pageSize int, results interface{}) PaginatedResponse {
	next := interface{}(nil)
	prev := interface{}(nil)

	totalPages := (count / int64(pageSize))
	if count%int64(pageSize) != 0 {
		totalPages++
	}

	if page < int(totalPages) {
		next = "page=" + string(rune(page+1))
	}
	if page > 1 {
		prev = "page=" + string(rune(page-1))
	}

	return PaginatedResponse{
		Count:    count,
		Next:     next,
		Previous: prev,
		Results:  results,
	}
}

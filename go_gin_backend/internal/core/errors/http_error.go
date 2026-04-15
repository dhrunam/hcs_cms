package errors

type HTTPError struct {
	Status  int    `json:"status"`
	Message string `json:"message"`
}

func (e HTTPError) Error() string {
	return e.Message
}

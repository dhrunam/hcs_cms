package audit

import "context"

type contextKey string

const userIDKey contextKey = "audit_user_id"

func WithUserID(ctx context.Context, userID string) context.Context {
	return context.WithValue(ctx, userIDKey, userID)
}

func UserID(ctx context.Context) string {
	value, _ := ctx.Value(userIDKey).(string)
	return value
}

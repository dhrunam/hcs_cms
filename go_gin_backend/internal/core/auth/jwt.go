package auth

import (
	"errors"
	"fmt"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

var ErrInvalidToken = errors.New("invalid token")

func ParseToken(tokenString string, secret string) (*Claims, error) {
	if strings.TrimSpace(tokenString) == "" || strings.TrimSpace(secret) == "" {
		return nil, ErrInvalidToken
	}

	claims := &Claims{}
	token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("%w: unsupported signing method", ErrInvalidToken)
		}
		return []byte(secret), nil
	})
	if err != nil {
		return nil, fmt.Errorf("%w: %v", ErrInvalidToken, err)
	}

	if !token.Valid {
		return nil, ErrInvalidToken
	}

	return claims, nil
}

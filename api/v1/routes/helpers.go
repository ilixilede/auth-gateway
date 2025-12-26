package authgateway

import (
	"context"
	"net/http"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/google/uuid"
	"auth-gateway/config"
	"auth-gateway/database"
)

type Token struct {
	AccessToken string `json:"access_token"`
	ExpiresIn  int    `json:"expires_in"`
	TokenType  string `json:"token_type"`
}

func GenerateToken(user database.User, expirationTime time.Time) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"username": user.Username,
		"exp":      expirationTime.Unix(),
	})

	tokenString, err := token.SignedString([]byte(config.Config().JWTSecret))
	if err != nil {
		return "", err
	}

	return tokenString, nil
}

func GenerateRefreshToken() (string, error) {
	return uuid.New().String(), nil
}

func VerifyToken(r *http.Request) (database.User, error) {
	tokenString := r.Header.Get("Authorization")
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error {
		_, ok := token.Method.(*jwt.SigningMethodHMAC)
		if !ok {
			return nil, errors.New("unexpected signing method")
		}

		return []byte(config.Config().JWTSecret), nil
	})

	if err != nil {
		return database.User{}, err
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		return database.User{
			Username: claims["username"].(string),
		}, nil
	} else {
		return database.User{}, errors.New("invalid token")
	}
}
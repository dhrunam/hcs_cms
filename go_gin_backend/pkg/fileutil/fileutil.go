package fileutil

import "path/filepath"

func Base(path string) string {
	return filepath.Base(path)
}

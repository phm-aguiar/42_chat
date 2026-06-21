package model

import (
	"crypto/rand"
	"encoding/binary"
	"fmt"
	"sync"
	"time"
)

// UUIDv7 generates a time-sortable UUID v7 string.
// Format: tttttttt-tttt-7rrr-rrrr-rrrrrrrrrrrr
// Where t = timestamp (Unix ms), r = random, 7 = version, r = variant (10xx)
//
// Uses stdlib only — no external dependencies.
// Thread-safe (mutex protects against timestamp collision in the same ms).
type uuidv7Generator struct {
	mu         sync.Mutex
	lastTime   int64
	clockSeq   uint16
}

var uuidv7 = &uuidv7Generator{}

// NewUUIDv7 returns a UUIDv7 string.
func NewUUIDv7() string {
	return uuidv7.generate()
}

func (g *uuidv7Generator) generate() string {
	g.mu.Lock()
	defer g.mu.Unlock()

	now := time.Now().UnixMilli()

	// Clock sequence: se mesmo ms, incrementa; se ms diferente, reseta
	if now == g.lastTime {
		g.clockSeq++
	} else {
		g.clockSeq = 0
		g.lastTime = now
	}

	// 6 bytes de timestamp (48 bits = ms desde epoch)
	ts := make([]byte, 6)
	binary.BigEndian.PutUint64(ts, uint64(now)<<16) // desloca pra caber em 6 bytes
	ts = ts[2:] // pega só os 6 bytes significativos

	// 2 bytes de clock sequence + random
	cs := make([]byte, 2)
	binary.BigEndian.PutUint16(cs, g.clockSeq)

	// 8 bytes de random
	randBytes := make([]byte, 8)
	if _, err := rand.Read(randBytes); err != nil {
		// fallback deterministico (não deve acontecer)
		for i := range randBytes {
			randBytes[i] = byte(time.Now().UnixNano() >> (i * 8))
		}
	}

	// Monta o UUID: 16 bytes
	uuid := make([]byte, 16)
	copy(uuid[0:6], ts)                          // timestamp (6 bytes)
	uuid[6] = (cs[0] & 0x0f) | 0x70              // version 7 (0111)
	uuid[7] = cs[1]                               // clock seq low
	uuid[8] = (randBytes[0] & 0x3f) | 0x80       // variant 10xx
	copy(uuid[9:16], randBytes[1:8])              // random rest

	return fmt.Sprintf("%08x-%04x-%04x-%04x-%012x",
		binary.BigEndian.Uint32(uuid[0:4]),
		binary.BigEndian.Uint16(uuid[4:6]),
		binary.BigEndian.Uint16(uuid[6:8]),
		binary.BigEndian.Uint16(uuid[8:10]),
		uuid[10:16],
	)
}

// IsValidUUID aceita v4 ou v7 (qualquer UUID RFC 4122).
func IsValidUUID(s string) bool {
	if len(s) != 36 {
		return false
	}
	for i, c := range s {
		switch i {
		case 8, 13, 18, 23:
			if c != '-' {
				return false
			}
		default:
			if !((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F')) {
				return false
			}
		}
	}
	return true
}

package sensor

import (
	"math/rand"
	"simulator/pkg/models"

	"github.com/google/uuid"
)

func newMachine() *models.Machine {
	return &models.Machine{
		ID:             uuid.New().String(),
		Name:           "Machine " + uuid.New().String(),
		Location:       "Location " + uuid.New().String(),
		Hours:          0,
		Degrade:        0.0,
		FaultThreshold: 0.8 + rand.Float64()*0.15,
	}
}

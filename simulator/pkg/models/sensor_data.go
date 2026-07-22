package models

import "time"

type SensorData struct {
	ID          string    `json:"id"`
	MachineID   string    `json:"machine_id"`
	Timestamp   time.Time `json:"timestamp"`
	Temperature float64   `json:"temperature"`
	Vibration   float64   `json:"vibration"`
	Pressure    float64   `json:"pressure"`
	Current     float64   `json:"current"`
	Hours       float64   `json:"hours"`
	IsFault     bool      `json:"is_fault"`
}

type Machine struct {
	ID             string  `json:"id"`
	Name           string  `json:"name"`
	Location       string  `json:"location"`
	Hours          float64 `json:"hours"`
	Degrade        float64 `json:"degrade"`
	FaultThreshold float64 `json:"fault_threshold"`
}

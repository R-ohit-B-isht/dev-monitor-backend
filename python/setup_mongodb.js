db = db.getSiblingDB('devin_tasks');

// Create monitoring_sessions collection
if (!db.getCollection('monitoring_sessions').exists()) {
    db.createCollection('monitoring_sessions');
}

// Add schema validation for monitoring_sessions
db.runCommand({
    collMod: 'monitoring_sessions',
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['engineerId', 'startTime', 'status'],
            properties: {
                engineerId: {
                    bsonType: 'string',
                    description: 'ID of the engineer being monitored'
                },
                startTime: {
                    bsonType: 'date',
                    description: 'When the monitoring session started'
                },
                endTime: {
                    bsonType: 'date',
                    description: 'When the monitoring session ended'
                },
                status: {
                    enum: ['running', 'stopped', 'idle'],
                    description: 'Current status of the monitoring session'
                },
                focusTime: {
                    bsonType: 'int',
                    description: 'Time spent focused on core tasks (in seconds)'
                },
                idleTime: {
                    bsonType: 'int',
                    description: 'Time spent idle (in seconds)'
                },
                productivityScore: {
                    bsonType: 'double',
                    minimum: 0,
                    maximum: 100,
                    description: 'Productivity score for this session'
                }
            }
        }
    }
});

// Create activity_events collection
if (!db.getCollection('activity_events').exists()) {
    db.createCollection('activity_events');
}

// Add schema validation for activity_events
db.runCommand({
    collMod: 'activity_events',
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['engineerId', 'sessionId', 'timestamp', 'eventType'],
            properties: {
                engineerId: {
                    bsonType: 'string',
                    description: 'ID of the engineer'
                },
                sessionId: {
                    bsonType: 'string',
                    description: 'ID of the monitoring session'
                },
                timestamp: {
                    bsonType: 'date',
                    description: 'When the event occurred'
                },
                eventType: {
                    enum: ['keyboard', 'mouse', 'ide', 'terminal', 'meeting', 'break'],
                    description: 'Type of activity event'
                },
                metadata: {
                    bsonType: 'object',
                    description: 'Additional event metadata'
                }
            }
        }
    }
});

// Create achievements collection
if (!db.getCollection('achievements').exists()) {
    db.createCollection('achievements');
}

// Add schema validation for achievements
db.runCommand({
    collMod: 'achievements',
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['engineerId', 'badge', 'earnedAt'],
            properties: {
                engineerId: {
                    bsonType: 'string',
                    description: 'ID of the engineer'
                },
                badge: {
                    enum: ['Daily Goal', 'Focus Master', 'Code Warrior', 'Team Player', 'Early Bird'],
                    description: 'Type of achievement badge'
                },
                earnedAt: {
                    bsonType: 'date',
                    description: 'When the badge was earned'
                },
                metadata: {
                    bsonType: 'object',
                    description: 'Additional achievement metadata'
                }
            }
        }
    }
});

// Create schedule_limits collection
if (!db.getCollection('schedule_limits').exists()) {
    db.createCollection('schedule_limits');
}

// Add schema validation for schedule_limits
db.runCommand({
    collMod: 'schedule_limits',
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['engineerId', 'dailyHourLimit', 'weeklyHourLimit'],
            properties: {
                engineerId: {
                    bsonType: 'string',
                    description: 'ID of the engineer'
                },
                dailyHourLimit: {
                    bsonType: 'int',
                    minimum: 1,
                    maximum: 24,
                    description: 'Maximum hours per day'
                },
                weeklyHourLimit: {
                    bsonType: 'int',
                    minimum: 1,
                    maximum: 168,
                    description: 'Maximum hours per week'
                },
                alertThreshold: {
                    bsonType: 'int',
                    minimum: 1,
                    maximum: 100,
                    description: 'Percentage threshold for alerts'
                }
            }
        }
    }
});

// Create indexes
db.monitoring_sessions.createIndex({ engineerId: 1, startTime: -1 });
db.monitoring_sessions.createIndex({ status: 1 });
db.activity_events.createIndex({ engineerId: 1, sessionId: 1, timestamp: -1 });
db.activity_events.createIndex({ eventType: 1 });
db.achievements.createIndex({ engineerId: 1, badge: 1 });
db.schedule_limits.createIndex({ engineerId: 1 });

from flask import Blueprint, jsonify, request, send_file
from datetime import datetime, timedelta
import pandas as pd
import io
from .monitoring_service import get_db

report_bp = Blueprint("report", __name__)

def generate_csv_report(data, filename="report.csv"):
    """Convert data to CSV format"""
    df = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output.getvalue()

@report_bp.route("/monitoring/report", methods=["GET"])
def generate_report():
    db = get_db()
    
    # Get query parameters
    start_date = request.args.get("startDate")
    end_date = request.args.get("endDate")
    report_type = request.args.get("type", "daily")  # daily, weekly, monthly
    format_type = request.args.get("format", "json")  # json, csv
    engineer_id = request.args.get("engineerId", "current")
    include_achievements = request.args.get("includeAchievements", "false") == "true"
    include_meetings = request.args.get("includeMeetings", "false") == "true"
    
    try:
        start = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # Base pipeline for monitoring sessions
    pipeline = [
        {
            "$match": {
                "startTime": {"$gte": start, "$lt": end},
                "engineerId": engineer_id,
                "status": {"$in": ["stopped", "idle"]}
            }
        }
    ]

    # Add grouping based on report type
    if report_type == "daily":
        pipeline.append({
            "$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$startTime"}},
                    "engineerId": "$engineerId"
                },
                "totalTime": {"$sum": "$focusTime"},
                "idleTime": {"$sum": "$idleTime"},
                "sessionCount": {"$sum": 1},
                "averageProductivity": {"$avg": "$productivityScore"}
            }
        })
    elif report_type == "weekly":
        pipeline.append({
            "$group": {
                "_id": {
                    "week": {"$week": "$startTime"},
                    "year": {"$year": "$startTime"},
                    "engineerId": "$engineerId"
                },
                "totalTime": {"$sum": "$focusTime"},
                "idleTime": {"$sum": "$idleTime"},
                "sessionCount": {"$sum": 1},
                "averageProductivity": {"$avg": "$productivityScore"}
            }
        })
    else:  # monthly
        pipeline.append({
            "$group": {
                "_id": {
                    "month": {"$month": "$startTime"},
                    "year": {"$year": "$startTime"},
                    "engineerId": "$engineerId"
                },
                "totalTime": {"$sum": "$focusTime"},
                "idleTime": {"$sum": "$idleTime"},
                "sessionCount": {"$sum": 1},
                "averageProductivity": {"$avg": "$productivityScore"}
            }
        })

    # Execute pipeline
    results = list(db.monitoring_sessions.aggregate(pipeline))

    # Add achievements if requested
    if include_achievements:
        for result in results:
            period_start = datetime.strptime(result["_id"]["date"], "%Y-%m-%d") if report_type == "daily" else start
            period_end = period_start + timedelta(days=1) if report_type == "daily" else end
            
            achievements = list(db.achievements.find({
                "engineerId": result["_id"]["engineerId"],
                "earnedAt": {"$gte": period_start, "$lt": period_end}
            }))
            result["achievements"] = [ach["badge"] for ach in achievements]

    # Add meeting data if requested
    if include_meetings:
        for result in results:
            period_start = datetime.strptime(result["_id"]["date"], "%Y-%m-%d") if report_type == "daily" else start
            period_end = period_start + timedelta(days=1) if report_type == "daily" else end
            
            meeting_tasks = list(db.tasks.find({
                "engineerId": result["_id"]["engineerId"],
                "createdAt": {"$gte": period_start, "$lt": period_end},
                "$or": [
                    {"title": {"$regex": "meeting|zoom|call|sync|standup|review", "$options": "i"}},
                    {"description": {"$regex": "meeting|zoom|call|sync|standup|review", "$options": "i"}}
                ]
            }))
            result["meetingCount"] = len(meeting_tasks)
            result["meetingTime"] = sum((task.get("duration", 0) for task in meeting_tasks), 0)

    # Format response
    if format_type == "csv":
        csv_data = generate_csv_report(results)
        output = io.StringIO()
        output.write(csv_data)
        output.seek(0)
        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"monitoring_report_{report_type}_{start.date()}_{end.date()}.csv"
        )

    return jsonify(results), 200

@report_bp.route("/monitoring/report/summary", methods=["GET"])
def get_report_summary():
    """Get a summary of available report metrics and time ranges"""
    return jsonify({
        "timeRanges": ["daily", "weekly", "monthly"],
        "metrics": [
            {"id": "focusTime", "name": "Focus Time", "type": "duration"},
            {"id": "idleTime", "name": "Idle Time", "type": "duration"},
            {"id": "productivityScore", "name": "Productivity Score", "type": "percentage"},
            {"id": "meetingTime", "name": "Meeting Time", "type": "duration"},
            {"id": "achievements", "name": "Achievements", "type": "list"}
        ],
        "formats": ["json", "csv"]
    }), 200

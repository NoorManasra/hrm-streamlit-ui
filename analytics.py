# === human_rights_api.py ===
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from datetime import datetime
from typing import Optional

client = MongoClient("mongodb+srv://admin:nqdoEbgeEWkp9dFI@hrm-cluster.3yb5td1.mongodb.net/?retryWrites=true&w=majority&appName=HRM-Cluster")
db = client.human_rights_db
cases_collection = db.cases

app = FastAPI()

@app.get("/analytics/violations")
async def get_violations_by_type(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    region: Optional[str] = Query(None)
):
    try:
        match_stage = {"archived": {"$ne": True}}

        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            match_stage["date_reported"] = {"$gte": start_dt}

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if "date_reported" in match_stage:
                match_stage["date_reported"]["$lte"] = end_dt
            else:
                match_stage["date_reported"] = {"$lte": end_dt}

        if region:
            match_stage["location.region"] = region

        pipeline = [
            {"$match": match_stage},
            {"$unwind": "$violation_types"},
            {"$group": {
                "_id": "$violation_types",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]

        result = list(cases_collection.aggregate(pipeline))
        return [{"violation_type": doc["_id"], "count": doc["count"]} for doc in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/geodata")
async def get_geodata(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    violation_type: Optional[str] = Query(None)
):
    try:
        match_stage = {"archived": {"$ne": True}}

        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            match_stage["date_reported"] = {"$gte": start_dt}

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if "date_reported" in match_stage:
                match_stage["date_reported"]["$lte"] = end_dt
            else:
                match_stage["date_reported"] = {"$lte": end_dt}

        if violation_type:
            match_stage["violation_types"] = violation_type

        pipeline = [
            {"$match": match_stage},
            {"$group": {
                "_id": {
                    "country": "$location.country",
                    "region": "$location.region",
                    "coordinates": "$location.coordinates.coordinates"
                },
                "count": {"$sum": 1}
            }}
        ]

        result = list(cases_collection.aggregate(pipeline))
        return [{
            "country": doc["_id"]["country"],
            "region": doc["_id"]["region"],
            "coordinates": doc["_id"]["coordinates"],
            "count": doc["count"]
        } for doc in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/timeline")
async def get_timeline(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    violation_type: Optional[str] = Query(None)
):
    try:
        match_stage = {"archived": {"$ne": True}}

        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            match_stage["date_reported"] = {"$gte": start_dt}

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if "date_reported" in match_stage:
                match_stage["date_reported"]["$lte"] = end_dt
            else:
                match_stage["date_reported"] = {"$lte": end_dt}

        if region:
            match_stage["location.region"] = region

        if violation_type:
            match_stage["violation_types"] = violation_type

        pipeline = [
            {"$match": match_stage},
            {"$group": {
                "_id": {
                    "year": {"$year": "$date_reported"},
                    "month": {"$month": "$date_reported"},
                    "day": {"$dayOfMonth": "$date_reported"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
        ]

        result = list(cases_collection.aggregate(pipeline))
        return [{
            "date": f"{doc['_id']['year']:04d}-{doc['_id']['month']:02d}-{doc['_id']['day']:02d}",
            "count": doc["count"]
        } for doc in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

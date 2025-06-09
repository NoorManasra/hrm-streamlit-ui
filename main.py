from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel, Field # type: ignore
from typing import List, Optional
from datetime import date
from pymongo import MongoClient # type: ignore
from bson import ObjectId # type: ignore
from fastapi import Path # type: ignore
from bson.errors import InvalidId # type: ignore
from datetime import datetime
from pydantic import BaseModel # type: ignore
from fastapi import Query # type: ignore
from fastapi import UploadFile, File # type: ignore

from analytics_api import analytics_router

app.include_router(analytics_router, prefix="/analytics")


app = FastAPI()

client = MongoClient("mongodb+srv://admin:nqdoEbgeEWkp9dFI@hrm-cluster.3yb5td1.mongodb.net/?retryWrites=true&w=majority&appName=HRM-Cluster")
db = client.human_rights_db
cases_collection = db.cases
status_history_collection = db.case_status_history


class StatusUpdate(BaseModel):
    new_status: str
class Coordinates(BaseModel):
    type: str
    coordinates: List[float] = Field(..., min_items=2, max_items=2)

class Location(BaseModel):
    country: str
    region: Optional[str]
    coordinates: Coordinates


class Perpetrator(BaseModel):
    name: str
    type: Optional[str]

from datetime import date
class Evidence(BaseModel):
    type: str
    url: str
    description: Optional[str]
    date_captured: Optional[date]


class Case(BaseModel):
    case_id: str
    title: str
    description: str
    violation_types: List[str]
    status: str
    priority: Optional[str]
    location: Location
    date_occurred: date
    date_reported: date
    victims: Optional[List[str]] 
    perpetrators: Optional[List[Perpetrator]]
    evidence: Optional[List[Evidence]]

def case_helper(case) -> dict:
    return {
        "id": str(case["_id"]),
        "case_id": case["case_id"],
        "title": case["title"],
        "description": case["description"],
        "violation_types": case["violation_types"],
        "status": case["status"],
        "priority": case.get("priority"),
        "location": case["location"],
        "date_occurred": case["date_occurred"],  
        "date_reported": case["date_reported"],
        "victims": case.get("victims"),
        "perpetrators": case.get("perpetrators"),
        "evidence": case.get("evidence"),
    }


#add case
@app.post("/cases/")
async def create_case(case: Case):
    case_dict = case.dict()

    case_dict["date_occurred"] = datetime.combine(case.date_occurred, datetime.min.time())
    case_dict["date_reported"] = datetime.combine(case.date_reported, datetime.min.time())

    if case_dict.get("evidence"):
        for ev in case_dict["evidence"]:
            if ev.get("date_captured"):
                ev["date_captured"] = datetime.combine(ev["date_captured"], datetime.min.time())

    result = cases_collection.insert_one(case_dict)
    new_case = cases_collection.find_one({"_id": result.inserted_id})
    return case_helper(new_case)

# retrive case by id
@app.get("/cases/{case_id}")
async def get_case(case_id: str = Path(..., description="The ID of the case to retrieve")):
    try:
        case = cases_collection.find_one({"_id": ObjectId(case_id), "archived": {"$ne": True}})
        if case:
            return case_helper(case)
        else:
            raise HTTPException(status_code=404, detail="Case not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid case ID")

# update case using put based on id
@app.put("/cases/{case_id}")
async def update_case(case_id: str, updated_case: Case):
    try:
        case_dict = updated_case.dict()
        case_dict["date_occurred"] = updated_case.date_occurred.isoformat()
        case_dict["date_reported"] = updated_case.date_reported.isoformat()

        if case_dict.get("evidence"):
            for ev in case_dict["evidence"]:
                if ev.get("date_captured") is not None:
                    ev["date_captured"] = ev["date_captured"].isoformat()

        result = cases_collection.update_one({"_id": ObjectId(case_id)}, {"$set": case_dict})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Case not found")
        updated = cases_collection.find_one({"_id": ObjectId(case_id)})
        return case_helper(updated)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid case ID")

# delete case based on its id
@app.delete("/cases/{case_id}")
async def archive_case(case_id: str):
    try:
        result = cases_collection.update_one(
            {"_id": ObjectId(case_id)},
            {"$set": {"archived": True}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Case not found")
        return {"detail": "Case archived successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid case ID")

    
#update case status based on its id
@app.patch("/cases/{case_id}/status")
async def update_case_status(case_id: str, status_update: StatusUpdate):
    try:
        case = cases_collection.find_one({"_id": ObjectId(case_id)})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        old_status = case["status"]
        new_status = status_update.new_status

        cases_collection.update_one(
            {"_id": ObjectId(case_id)},
            {"$set": {"status": new_status}}
        )

        status_history_collection.insert_one({
            "case_id": case["case_id"],
            "old_status": old_status,
            "new_status": new_status,
            "changed_at": datetime.utcnow().isoformat()
        })

        return {"detail": "Case status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/cases/")
async def get_cases(
    date_occurred: Optional[str] = Query(None, description="Filter by date_occurred, format YYYY-MM-DD"),
    country: Optional[str] = Query(None, description="Filter by country"),
    region: Optional[str] = Query(None, description="Filter by region"),
    violation_type: Optional[str] = Query(None, description="Filter by violation type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(10, ge=1, le=100, description="Number of cases to return"),
    skip: int = Query(0, ge=0, description="Number of cases to skip"),
):
    filter_query = {"archived": {"$ne": True}}

    if date_occurred:
        try:
            date_obj = datetime.strptime(date_occurred, "%Y-%m-%d")
            next_day = date_obj.replace(hour=23, minute=59, second=59)
            filter_query["date_occurred"] = {
                "$gte": date_obj,
                "$lte": next_day
            }
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_occurred format, should be YYYY-MM-DD")

    if country:
        filter_query["location.country"] = {"$regex": f"^{country}$", "$options": "i"}

    if region:
        filter_query["location.region"] = {"$regex": f"^{region}$", "$options": "i"}

    if violation_type:
        filter_query["violation_types"] = {"$in": [violation_type]}

    if priority:
        filter_query["priority"] = {"$regex": f"^{priority}$", "$options": "i"}

    cases = []
    cursor = cases_collection.find(filter_query).skip(skip).limit(limit)
    for case in cursor:
        cases.append(case_helper(case))
    return cases


@app.get("/cases/{case_id}/status-history")
async def get_status_history(case_id: str):
    case = cases_collection.find_one({"_id": ObjectId(case_id)})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    history = list(status_history_collection.find({"case_id": case["case_id"]}).sort("changed_at", 1))
    for record in history:
        record["_id"] = str(record["_id"])
        if isinstance(record["changed_at"], datetime):
            record["changed_at"] = record["changed_at"].isoformat()
    return history


@app.post("/cases/{case_id}/upload")
async def upload_files(case_id: str, files: List[UploadFile] = File(...)):
    try:
        case = cases_collection.find_one({"_id": ObjectId(case_id)})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        


        uploaded_urls = []
        for file in files:
            file_location = f"uploads/{case_id}_{file.filename}"
            with open(file_location, "wb") as f:
                content = await file.read()
                f.write(content)
            uploaded_urls.append(file_location) 

        new_evidence = [{"type": "file", "url": url} for url in uploaded_urls]
        cases_collection.update_one(
            {"_id": ObjectId(case_id)},
            {"$push": {"evidence": {"$each": new_evidence}}}
        )

        return {"detail": "Files uploaded successfully", "files": uploaded_urls}

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid case ID")

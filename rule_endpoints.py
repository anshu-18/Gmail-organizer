from fastapi import FastAPI, Path, Query, HTTPException
from typing import Annotated
from pydantic import BaseModel

from connection_string import MONGO_URI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI(
    title="Gmail API Rule Endpoints",
    description="Endpoints for managing Gmail rules and labels"
)

class Rule(BaseModel):
    label: str | None = None
    keywords: list[str] = []

client = AsyncIOMotorClient(MONGO_URI)
db = client["GMAIL_RULES_DB"]
collection = db["labels_keywords"]

#only unique labels exists
collection.create_index("label", unique=True)

@app.post("/rules")
async def create_rule(rule: Rule):
    try:
        existing_rules = await collection.find().to_list(length=None)

        for r in existing_rules:
            if r["label"].lower() == rule.label.lower():
                r["keywords"].extend(rule.keywords)
                updated_keywords = list(set(r["keywords"])) #Remove duplicates keywords
                print(updated_keywords)
                res = await collection.update_one(
                    {"label": rule.label.lower()},
                    {"$set": {"keywords": updated_keywords}}
                )
                return {"message": "Rule updated successfully", "rule_id": str(res.upserted_id)}
        
        # If no existing rule matches, create a new one
        rule.label = rule.label.lower()  # Ensure label is lowercase
        rule.keywords = list(set(rule.keywords))  # Remove duplicates keywords
        res = await collection.insert_one(rule.dict())
        return {"message": "Rule created successfully", "rule_id": str(res.inserted_id)}
    except Exception as e:
        print(f"Rule already exists or failed inserting data: {e}")
        raise HTTPException(status_code=400, detail="Rule already exists")
    
@app.put("/rules/{rule_id}")
async def update_rule(rule_id: Annotated[str, Path(title="Rule_id", description="rule to be updated")],
                      updated_rule: Annotated[list[str], Query(description="List of keywords to be updated")]):
    try:
        existing_rule = await collection.find().to_list(length=None)

        for e_r in existing_rule:
            if e_r["label"].lower() == rule_id.lower():
                for keywd in updated_rule:
                    if keywd not in e_r["keywords"]:
                        e_r["keywords"].append(keywd)
                res = await collection.update_one(
                     {"label": rule_id.lower()},
                     {"$set": {"keywords": e_r["keywords"]}}
                )
    except Exception as e:
        print(f"Rule update failed: {e}")
        raise HTTPException(status_code=400, detail="Rule update failed")

#delete the label    
@app.delete("/rules/{rule_id}")
async def delete_label_rule(rule_id: Annotated[str, Path(title="Rule_id", description="rule to be deleted")]):
    try:
        res = await collection.find_one({"label": rule_id.lower()})
        if res is None:
            raise HTTPException(status_code=404, detail="Rule not found")
        else:
            await collection.delete_one({"label": rule_id.lower()})
            return {"message": "Rule deleted successfully"}
    except Exception as e:
        print(f"Rule deletion failed: {e}")

#delete the label with particular keyword
@app.delete("/rules")
async def delete_label_with_particular_keywd(keywd: Annotated[str, Query(title="keyword", description="delete the label with particular keyword")]):
    try:
        existing_rule = await collection.find().to_list(length=None)

        for e_r in existing_rule:
            if keywd in e_r["keywords"]:
                await collection.delete_one(
                    {"label": e_r["label"].lower()}
                )
                return {"message": "Rule with '{keywd}' keyword deleted successfully"}
    except Exception as e:
        print(f"Rule deletion with keyword failed: {e}")
        raise HTTPException(status_code=400, detail="Rule deletion with keyword failed")
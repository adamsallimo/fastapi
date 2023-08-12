from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

origins = [
    "https://c-room.vercel.app/",
    "http://localhost:3000",  
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Classroom(BaseModel):
    name: str
    subject: str
    image: str

class Post(BaseModel):
    authorId: str
    idClass: str
    date: str
    post: str

class Post(BaseModel):
    class_id: str
    author_id: str
    post: str

class Comment(BaseModel):
    post_id: str
    author_id: str
    comment: str

client = MongoClient("mongodb://mongo:d4U1UceJgBmKhNGnyPSj@containers-us-west-79.railway.app:6138")
db = client["classroom"]
collection = db["class"]
userCollection = db["users"]
postCollection = db["post"]  
commentsCollection = db["comments"]  

class Fish(BaseModel):
    hello: str

@app.get("/class/{class_id}")
def read_class_with_posts(class_id: str):
    try:
        class_id_obj = ObjectId(class_id)
        
        classroom = collection.find_one({"_id": class_id_obj})
        if classroom:
            classroom["_id"] = str(classroom["_id"])
            
            posts = list(postCollection.find({"idClass": class_id}))
            serialized_posts = []
            for post in posts:
                post["_id"] = str(post["_id"])
                post.pop("idClass", None)
                
                author_id = post["authorId"]
                user_data = userCollection.find_one({"_id": ObjectId(author_id)})
                if user_data:
                    user_data["_id"] = str(user_data["_id"])
                    post["user"] = user_data
                
                comment_id = post["_id"]
                comments = commentsCollection.find({"post_id": comment_id})
                serialized_comments = []
                for comment_data in comments:
                    comment_data["_id"] = str(comment_data["_id"])
                    comment_author_id = comment_data["author_id"]
                    comment_user_data = userCollection.find_one({"_id": ObjectId(comment_author_id)})
                    if comment_user_data:
                        comment_user_data["_id"] = str(comment_user_data["_id"])
                        comment_data["user"] = comment_user_data
                    serialized_comments.append(comment_data)
                post["comments"] = serialized_comments
                
                serialized_posts.append(post)

            
            classroom["posts"] = serialized_posts
            
            return classroom
        else:
            return {"error": 404}
    except Exception as e:
        return {"message": str(e)}



@app.get("/users/{user_id}")
def read_user(user_id: str):
    try:
        user_id_obj = ObjectId(user_id)
        user = userCollection.find_one({"_id": user_id_obj})
        if user:
            user["_id"] = str(user["_id"])
            return user
        else:
            return {"error": 404}
    except Exception as e:
        return {"message": str(e)}


@app.get("/class")
def read_all_classes():
    all_classes = list(collection.find())
    serialized_classes = []
    for class_data in all_classes:
        class_data["_id"] = str(class_data["_id"])
        serialized_classes.append(class_data)

    if serialized_classes:
        return serialized_classes
    else:
        return {"error": 404}


@app.post("/class/create")
def create_class(classroom: Classroom):
    new_class = {
        "name": classroom.name,
        "subject": classroom.subject,
        "image": classroom.image
    }
    result = collection.insert_one(new_class)
    return {"id": str(result.inserted_id)}


@app.put("/class/{fish_id}")
def update_class(fish_id: str, classroom: Classroom):
    try:
        fish_id_obj = ObjectId(fish_id)
        updated_class = {
            "name": classroom.name,
            "subject": classroom.subject
        }
        result = collection.update_one({"_id": fish_id_obj}, {"$set": updated_class})

        if result.matched_count > 0:
            return {"message": "Class updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Class not found")
    except Exception as e:
        return {"message": str(e)}



@app.get("/post/{class_id}")
def read_posts_by_class(class_id: str):
    try:
        class_id_obj = class_id
        
        posts = list(postCollection.find({"idClass": class_id_obj}))
        
        if posts:
            for post in posts:
                post["_id"] = str(post["_id"])
            return posts
        else:
            return {"error": f"No posts found for the class ID: {class_id}"}
    except Exception as e:
        return {"error": str(e)}



@app.post("/post/create")
def create_post(post: Post):
    new_class = {
        "authorId": post.author_id,
        "idClass": post.class_id,
        "post": post.post,
        "date": datetime.now().isoformat() 
    }
    
    result = postCollection.insert_one(new_class)
    return {"id": str(result.inserted_id)}


@app.post("/comment/create")
def create_comment(comment: Comment):
    new_class = {
        "author_id": comment.author_id,
        "post_id": comment.post_id,
        "comment": comment.comment,
        "date": datetime.now().isoformat() 
    }
    
    result = commentsCollection.insert_one(new_class)
    return {"id": str(result.inserted_id)}

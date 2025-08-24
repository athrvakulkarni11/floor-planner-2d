from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import requests
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
load_dotenv()
GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")

# Create directories for static files and templates
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app = FastAPI(
    title="Blueprint Generator API",
    description="AI-powered architectural blueprint generation system",
    version="2.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Expanded building types
BUILDING_TYPES = [
    "residential_house",
    "apartment_complex", 
    "office_building",
    "retail_store",
    "restaurant",
    "warehouse",
    "school",
    "hospital",
    "clinic",
    "hotel",
    "shopping_mall",
    "gym_fitness_center",
    "library",
    "community_center",
    "industrial_facility"
]

# Room directions
ROOM_DIRECTIONS = ["North", "South", "East", "West", "Northeast", "Northwest", "Southeast", "Southwest", "Center"]

# Pydantic models for API
class BuildingRequirements(BaseModel):
    building_type: str
    total_area: float
    floors: int
    occupancy: str
    special_features: List[str]
    budget_level: str = "standard"

class DesignFeedback(BaseModel):
    feedback: str
    session_id: str

class OptimizationRequest(BaseModel):
    goals: List[str]

class FloorUpdateRequest(BaseModel):
    floor_number: int
    session_id: str

class BlueprintResponse(BaseModel):
    success: bool
    blueprint: Optional[Dict] = None
    message: str
    version: int
    timestamp: str
    session_id: Optional[str] = None

# Global storage for demo purposes (use database in production)
design_storage = {}

class GeminiBlueprintGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        self.design_history = []
        self.current_floor = 1
        
    def generate_initial_blueprint(self, requirements: BuildingRequirements) -> Dict:
        """Generate initial blueprint based on requirements"""
        prompt = self._generate_initial_prompt(requirements)
        response = self._call_gemini_api(prompt)
        blueprint = self._parse_blueprint_response(response)
        
        # Ensure proper floor structure
        blueprint = self._validate_and_fix_blueprint(blueprint, requirements)
        
        # Store in history
        self.design_history.append({
            "version": 1,
            "blueprint": blueprint,
            "feedback": "Initial generation",
            "timestamp": datetime.now().isoformat(),
            "changes_made": ["Initial creation"],
            "current_floor": 1
        })
        
        return blueprint
    
    def iterate_design(self, user_feedback: str) -> Dict:
        """Iterate on existing design based on user feedback"""
        if not self.design_history:
            raise ValueError("No existing design to iterate on")
            
        current_design = self.design_history[-1]["blueprint"]
        prompt = self._generate_iteration_prompt(current_design, user_feedback)
        response = self._call_gemini_api(prompt)
        updated_blueprint = self._parse_blueprint_response(response)
        
        # Validate and maintain floor structure
        updated_blueprint = self._validate_and_fix_blueprint(updated_blueprint, None)
        
        # Store iteration
        self.design_history.append({
            "version": len(self.design_history) + 1,
            "blueprint": updated_blueprint,
            "feedback": user_feedback,
            "timestamp": datetime.now().isoformat(),
            "changes_made": ["User feedback integration"],
            "current_floor": self.current_floor
        })
        
        return updated_blueprint
    
    def update_floor_view(self, floor_number: int) -> Dict:
        """Update current floor view without changing the blueprint"""
        if not self.design_history:
            raise ValueError("No existing design to view")
            
        self.current_floor = floor_number
        current_blueprint = self.design_history[-1]["blueprint"]
        
        # Update current floor in history
        self.design_history[-1]["current_floor"] = floor_number
        
        return current_blueprint
    
    def optimize_design(self, optimization_goals: List[str]) -> Dict:
        """Optimize design for specific goals"""
        if not self.design_history:
            raise ValueError("No existing design to optimize")
            
        current_design = self.design_history[-1]["blueprint"]
        prompt = self._generate_optimization_prompt(current_design, optimization_goals)
        response = self._call_gemini_api(prompt)
        optimized_blueprint = self._parse_blueprint_response(response)
        
        # Validate and maintain floor structure
        optimized_blueprint = self._validate_and_fix_blueprint(optimized_blueprint, None)
        
        # Store optimization
        self.design_history.append({
            "version": len(self.design_history) + 1,
            "blueprint": optimized_blueprint,
            "feedback": f"Optimization for: {', '.join(optimization_goals)}",
            "timestamp": datetime.now().isoformat(),
            "changes_made": ["Design optimization"],
            "current_floor": self.current_floor
        })
        
        return optimized_blueprint
    
    def _validate_and_fix_blueprint(self, blueprint: Dict, requirements: Optional[BuildingRequirements]) -> Dict:
        """Validate and fix blueprint structure"""
        # Ensure all rooms have directions
        for floor_plan in blueprint.get("floor_plans", []):
            for room in floor_plan.get("rooms", []):
                if "direction" not in room:
                    # Assign direction based on position
                    room["direction"] = self._calculate_room_direction(room)
                
                # Ensure room has all required fields
                if "features" not in room:
                    room["features"] = []
                if "color" not in room:
                    room["color"] = self._get_default_room_color(room.get("type", "general"))
        
        return blueprint
    
    def _calculate_room_direction(self, room: Dict) -> str:
        """Calculate room direction based on position"""
        pos = room.get("position", {"x": 0, "y": 0})
        x, y = pos.get("x", 0), pos.get("y", 0)
        
        # Simple direction calculation based on position
        if x < -5 and y > 5:
            return "Northwest"
        elif x > 5 and y > 5:
            return "Northeast"
        elif x < -5 and y < -5:
            return "Southwest"
        elif x > 5 and y < -5:
            return "Southeast"
        elif x < -2:
            return "West"
        elif x > 2:
            return "East"
        elif y > 2:
            return "North"
        elif y < -2:
            return "South"
        else:
            return "Center"
    
    def _get_default_room_color(self, room_type: str) -> str:
        """Get default color for room type"""
        color_map = {
            "living": "#e3f2fd",
            "bedroom": "#f3e5f5",
            "kitchen": "#e8f5e8",
            "bathroom": "#fff3e0",
            "office": "#e1f5fe",
            "dining": "#fce4ec",
            "storage": "#f5f5f5",
            "hallway": "#f9f9f9",
            "lobby": "#e0f2f1",
            "conference": "#fff8e1",
            "medical": "#e8eaf6",
            "lab": "#f1f8e9",
            "ward": "#fafafa"
        }
        return color_map.get(room_type, "#f5f5f5")
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Make API call to Gemini"""
        url = f"{self.base_url}?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
                "responseMimeType": "text/plain"
            }
        }
        
        try:
            response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'candidates' in response_data and len(response_data['candidates']) > 0:
                    return response_data['candidates'][0]['content']['parts'][0]['text']
                else:
                    raise Exception("No response generated by Gemini")
            else:
                raise Exception(f"API call failed: {response.status_code} - {response.text}")
        except Exception as e:
            # Fallback response for demo purposes
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Fallback response when API fails"""
        return '''
{
  "building_info": {
    "type": "residential_house",
    "total_area": 150.0,
    "floors": 2,
    "occupancy": "family",
    "special_features": ["parking", "garden"],
    "budget_level": "standard"
  },
  "floor_plans": [
    {
      "floor_number": 1,
      "area": 75.0,
      "rooms": [
        {
          "name": "Living Room",
          "type": "living",
          "dimensions": {
            "width": 6.0,
            "length": 8.0,
            "area": 48.0
          },
          "position": {
            "x": 0,
            "y": 0
          },
          "direction": "Center",
          "features": ["natural_light", "main_entrance"],
          "color": "#e3f2fd"
        },
        {
          "name": "Kitchen",
          "type": "kitchen", 
          "dimensions": {
            "width": 4.0,
            "length": 5.0,
            "area": 20.0
          },
          "position": {
            "x": 8,
            "y": 0
          },
          "direction": "East",
          "features": ["ventilation", "plumbing"],
          "color": "#e8f5e8"
        }
      ]
    },
    {
      "floor_number": 2,
      "area": 75.0,
      "rooms": [
        {
          "name": "Master Bedroom",
          "type": "bedroom",
          "dimensions": {
            "width": 5.0,
            "length": 6.0,
            "area": 30.0
          },
          "position": {
            "x": 0,
            "y": 0
          },
          "direction": "North",
          "features": ["natural_light", "ensuite"],
          "color": "#f3e5f5"
        }
      ]
    }
  ],
  "design_constraints": {
    "building_codes": ["local_residential_code"],
    "min_room_dimensions": {
      "bedroom": {"min_area": 12, "min_width": 3},
      "bathroom": {"min_area": 6, "min_width": 2}
    }
  },
  "metadata": {
    "created_date": "2025-01-01T00:00:00",
    "version": "1.0",
    "generator": "Gemini Blueprint System"
  }
}
'''
    
    def _parse_blueprint_response(self, response: str) -> Dict:
        """Parse and validate blueprint JSON response"""
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            # Return fallback blueprint
            return json.loads(self._get_fallback_response())
    
    def _generate_initial_prompt(self, requirements: BuildingRequirements) -> str:
        """Generate initial blueprint creation prompt"""
        room_suggestions = self._get_room_suggestions(requirements.building_type)
        
        return f"""
You are an expert architect. Create a detailed architectural blueprint in JSON format for a {requirements.building_type} building.

Requirements:
- Building Type: {requirements.building_type}
- Total Area: {requirements.total_area} square meters
- Number of Floors: {requirements.floors}
- Occupancy: {requirements.occupancy}
- Special Features: {', '.join(requirements.special_features)}
- Budget Level: {requirements.budget_level}

Suggested rooms for {requirements.building_type}: {', '.join(room_suggestions)}

Return a JSON blueprint with this exact structure and include ALL {requirements.floors} floors:
{{
  "building_info": {{
    "type": "{requirements.building_type}",
    "total_area": {requirements.total_area},
    "floors": {requirements.floors},
    "occupancy": "{requirements.occupancy}",
    "special_features": {requirements.special_features},
    "budget_level": "{requirements.budget_level}"
  }},
  "floor_plans": [
    {{
      "floor_number": 1,
      "area": {requirements.total_area / requirements.floors},
      "rooms": [
        {{
          "name": "Room Name",
          "type": "room_type",
          "dimensions": {{
            "width": 6.0,
            "length": 8.0,
            "area": 48.0
          }},
          "position": {{
            "x": 0,
            "y": 0
          }},
          "direction": "North|South|East|West|Northeast|Northwest|Southeast|Southwest|Center",
          "features": ["feature1", "feature2"],
          "color": "#hexcolor"
        }}
      ]
    }}
  ],
  "design_constraints": {{
    "building_codes": ["relevant_building_codes"],
    "min_room_dimensions": {{
      "bedroom": {{"min_area": 12, "min_width": 3}},
      "bathroom": {{"min_area": 6, "min_width": 2}}
    }}
  }},
  "metadata": {{
    "created_date": "{datetime.now().isoformat()}",
    "version": "1.0",
    "generator": "Gemini Blueprint System"
  }}
}}

IMPORTANT:
1. Include exactly {requirements.floors} floor plans in the floor_plans array
2. Each room MUST have a "direction" field with one of: North, South, East, West, Northeast, Northwest, Southeast, Southwest, Center
3. Distribute the total area ({requirements.total_area} sq m) across all floors
4. Use appropriate room types and colors for {requirements.building_type}
5. Position rooms logically and ensure they don't overlap

Return only the JSON, no additional text.
"""
    
    def _get_room_suggestions(self, building_type: str) -> List[str]:
        """Get suggested rooms based on building type"""
        suggestions = {
            "residential_house": ["living_room", "kitchen", "bedrooms", "bathrooms", "dining_room"],
            "hospital": ["reception", "waiting_area", "examination_rooms", "wards", "operating_theater", "pharmacy", "laboratory"],
            "office_building": ["reception", "offices", "conference_rooms", "break_room", "storage"],
            "school": ["classrooms", "library", "cafeteria", "gymnasium", "administration_office"],
            "restaurant": ["dining_area", "kitchen", "storage", "restrooms", "bar_area"],
            "hotel": ["lobby", "guest_rooms", "restaurant", "conference_rooms", "fitness_center"]
        }
        return suggestions.get(building_type, ["main_area", "secondary_areas", "utilities"])
    
    def _generate_iteration_prompt(self, current_blueprint: Dict, user_feedback: str) -> str:
        """Generate iteration prompt"""
        return f"""
Modify this architectural blueprint based on user feedback. Maintain the multi-floor structure and room directions.

Current Blueprint:
{json.dumps(current_blueprint, indent=2)}

User Feedback:
{user_feedback}

IMPORTANT:
1. Keep the same number of floors as in the original blueprint
2. Each room MUST have a "direction" field
3. Update room positions, dimensions, and colors as needed based on feedback
4. Maintain logical room placement and avoid overlaps
5. Keep the same JSON structure

Return only the updated JSON blueprint, no additional text.
"""
    
    def _generate_optimization_prompt(self, current_blueprint: Dict, optimization_goals: List[str]) -> str:
        """Generate optimization prompt"""
        return f"""
Optimize this architectural blueprint for these goals while maintaining structure and room directions.

Current Blueprint:
{json.dumps(current_blueprint, indent=2)}

Optimization Goals:
{chr(10).join([f"- {goal}" for goal in optimization_goals])}

IMPORTANT:
1. Keep the same number of floors
2. Each room MUST have a "direction" field
3. Optimize room sizes, positions, and features based on goals
4. Maintain the same JSON structure

Return only the optimized JSON blueprint, no additional text.
"""

# Initialize generator
generator = GeminiBlueprintGenerator(GEMINI_API_KEY)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main UI"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/building-types")
async def get_building_types():
    """Get available building types"""
    return {"building_types": BUILDING_TYPES}

@app.post("/api/generate", response_model=BlueprintResponse)
async def generate_blueprint(requirements: BuildingRequirements):
    """Generate initial blueprint"""
    try:
        if requirements.building_type not in BUILDING_TYPES:
            raise HTTPException(status_code=400, detail="Invalid building type")
            
        blueprint = generator.generate_initial_blueprint(requirements)
        session_id = str(uuid.uuid4())
        design_storage[session_id] = generator.design_history.copy()
        
        return BlueprintResponse(
            success=True,
            blueprint=blueprint,
            message="Blueprint generated successfully",
            version=1,
            timestamp=datetime.now().isoformat(),
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/iterate", response_model=BlueprintResponse)
async def iterate_blueprint(feedback: DesignFeedback):
    """Iterate on existing blueprint"""
    try:
        if feedback.session_id not in design_storage:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Restore generator state
        generator.design_history = design_storage[feedback.session_id]
        blueprint = generator.iterate_design(feedback.feedback)
        design_storage[feedback.session_id] = generator.design_history.copy()
        
        return BlueprintResponse(
            success=True,
            blueprint=blueprint,
            message="Blueprint updated successfully based on feedback",
            version=len(generator.design_history),
            timestamp=datetime.now().isoformat(),
            session_id=feedback.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-floor", response_model=BlueprintResponse)
async def update_floor_view(floor_request: FloorUpdateRequest):
    """Update floor view"""
    try:
        if floor_request.session_id not in design_storage:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Restore generator state
        generator.design_history = design_storage[floor_request.session_id]
        blueprint = generator.update_floor_view(floor_request.floor_number)
        design_storage[floor_request.session_id] = generator.design_history.copy()
        
        return BlueprintResponse(
            success=True,
            blueprint=blueprint,
            message=f"Floor {floor_request.floor_number} view updated",
            version=len(generator.design_history),
            timestamp=datetime.now().isoformat(),
            session_id=floor_request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize", response_model=BlueprintResponse)
async def optimize_blueprint(session_id: str, optimization: OptimizationRequest):
    """Optimize blueprint"""
    try:
        if session_id not in design_storage:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Restore generator state
        generator.design_history = design_storage[session_id]
        blueprint = generator.optimize_design(optimization.goals)
        design_storage[session_id] = generator.design_history.copy()
        
        return BlueprintResponse(
            success=True,
            blueprint=blueprint,
            message="Blueprint optimized successfully",
            version=len(generator.design_history),
            timestamp=datetime.now().isoformat(),
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{session_id}")
async def get_design_history(session_id: str):
    """Get design iteration history"""
    if session_id not in design_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"history": design_storage[session_id]}

@app.get("/api/current-floor/{session_id}")
async def get_current_floor(session_id: str):
    """Get current floor number"""
    if session_id not in design_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = design_storage[session_id]
    current_floor = 1
    if history:
        current_floor = history[-1].get("current_floor", 1)
    
    return {"current_floor": current_floor}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
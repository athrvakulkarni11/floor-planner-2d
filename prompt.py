"""
LLM Prompt System for Blueprint Generation
Designed for Groq Cloud GPT models
"""

class BlueprintPromptGenerator:
    def __init__(self):
        self.system_prompt = """
You are an expert architect and building designer specializing in creating detailed floor plans. 
Your role is to generate precise, code-compliant building layouts in JSON format.

CORE PRINCIPLES:
1. Follow building codes (IBC, ADA compliance)
2. Ensure logical flow and functionality
3. Optimize space utilization
4. Consider safety (egress, fire exits)
5. Include proper utilities and structural elements

DIMENSIONAL STANDARDS:
- Residential bedroom: min 7 sq.m, min width 2.4m
- Bathroom: min 3 sq.m, accessible 5 sq.m
- Kitchen: min 6 sq.m for functionality
- Corridors: min 1.2m, recommended 1.5m
- Doors: standard 0.9m, accessible 1.0m
- Ceiling heights: residential 2.4m, commercial 3.0m+

Always respond in valid JSON format matching the provided schema.
"""

    def generate_initial_prompt(self, building_type, requirements):
        """Generate initial blueprint creation prompt"""
        return f"""
{self.system_prompt}

TASK: Generate a complete floor plan for a {building_type}.

REQUIREMENTS:
- Building type: {building_type}
- Total area: {requirements.get('total_area', 'not specified')} sq.m
- Number of floors: {requirements.get('floors', 1)}
- Special requirements: {requirements.get('special_features', 'none')}
- Occupancy: {requirements.get('occupancy', 'not specified')}
- Budget considerations: {requirements.get('budget_level', 'standard')}

SPECIFIC NEEDS FOR {building_type.upper()}:
{self._get_building_specific_requirements(building_type)}

Generate a complete JSON blueprint following the schema. Ensure all dimensions are realistic and code-compliant.
"""

    def generate_iteration_prompt(self, current_design, user_feedback):
        """Generate prompt for design iterations"""
        return f"""
{self.system_prompt}

TASK: Modify the existing blueprint based on user feedback.

CURRENT DESIGN:
{current_design}

USER FEEDBACK:
{user_feedback}

INSTRUCTIONS:
1. Analyze the feedback and identify specific changes needed
2. Modify only the affected areas while maintaining overall design integrity
3. Ensure changes don't violate building codes or create safety issues
4. Maintain proper relationships between rooms and circulation
5. Update dimensions, positions, and connections as needed

Return the complete updated JSON blueprint.
"""

    def _get_building_specific_requirements(self, building_type):
        """Get specific requirements based on building type"""
        requirements = {
            'hospital': """
- Patient rooms: min 12 sq.m single, 18 sq.m double
- Corridors: min 2.4m wide for bed access
- Nurse stations: central visibility
- Emergency exits: multiple egress paths
- Specialized rooms: OR, ICU, pharmacy, lab
- Utility rooms: medical gas, electrical, housekeeping
- Infection control: proper ventilation zones
""",
            'residential': """
- Bedrooms: privacy and natural light
- Kitchen: work triangle efficiency
- Living areas: social interaction spaces
- Storage: minimum 10% of floor area
- Bathrooms: proper ventilation
- Entry: transition space from exterior
- Circulation: minimize corridor space
""",
            'office': """
- Open office: 6-10 sq.m per workstation
- Meeting rooms: various sizes for teams
- Break rooms: social and food prep areas
- Reception: welcoming entrance
- Storage: filing and supplies
- Server room: climate controlled
- Accessibility: ADA compliant throughout
""",
            'educational': """
- Classrooms: 2 sq.m per student minimum
- Wide corridors: 3m+ for student flow
- Emergency exits: maximum 45m travel distance
- Specialized rooms: labs, library, gym
- Administrative offices: principal, counselors
- Accessibility: full ADA compliance
- Safety: secure entrances, sight lines
"""
        }
        return requirements.get(building_type, "Standard commercial requirements apply.")

    def generate_optimization_prompt(self, design, optimization_goals):
        """Generate prompt for design optimization"""
        return f"""
{self.system_prompt}

TASK: Optimize the existing design for specific goals.

CURRENT DESIGN:
{design}

OPTIMIZATION GOALS:
{optimization_goals}

OPTIMIZATION FOCUS AREAS:
1. Space efficiency - eliminate wasted areas
2. Traffic flow - optimize circulation patterns
3. Natural light - maximize window placement
4. Cost efficiency - reduce complex shapes
5. Functionality - improve room relationships
6. Code compliance - ensure all requirements met

Analyze each room and circulation area. Propose improvements while maintaining the core program requirements.
Return the optimized JSON blueprint.
"""

# Example usage
prompt_generator = BlueprintPromptGenerator()

# Example requirements
requirements = {
    'total_area': 200,
    'floors': 1,
    'special_features': ['wheelchair_accessible', 'family_friendly'],
    'occupancy': '4 people',
    'budget_level': 'moderate'
}

# Generate initial prompt
initial_prompt = prompt_generator.generate_initial_prompt('residential', requirements)
print("=== INITIAL PROMPT ===")
print(initial_prompt)
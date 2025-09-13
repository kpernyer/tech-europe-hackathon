#!/usr/bin/env python3
"""
Enhanced Communication Flow Generator
Implements three-level authority system, catch-ball tracking, and wisdom-of-the-crowd patterns
for Living Twin synthetic organizations.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
from enum import Enum

class AuthorityLevel(Enum):
    """Three levels of downward organizational communication."""
    NUDGE = "nudge"        # Gentle suggestion, high autonomy
    RECOMMEND = "recommend" # Strong suggestion with rationale
    ORDER = "order"        # Direct command, compliance expected

class CommunicationStyle(Enum):
    """Different communication patterns in organizations."""
    HIERARCHICAL = "hierarchical"    # Top-down delegation
    CATCH_BALL = "catch_ball"       # Back-and-forth refinement
    GOSSIP = "gossip"               # Lateral wisdom-of-the-crowd

class EnhancedCommunicationFlow:
    """Generates sophisticated organizational communication patterns."""
    
    def __init__(self):
        self.authority_patterns = {
            AuthorityLevel.NUDGE: {
                "language_style": "suggestive",
                "autonomy_level": 0.8,
                "compliance_expectation": 0.3,
                "response_required": False,
                "phrases": [
                    "You might want to consider...",
                    "It could be valuable to explore...",
                    "Have you thought about...",
                    "When you have a moment, perhaps..."
                ]
            },
            AuthorityLevel.RECOMMEND: {
                "language_style": "advisory",
                "autonomy_level": 0.5,
                "compliance_expectation": 0.7,
                "response_required": True,
                "phrases": [
                    "I strongly recommend...",
                    "Based on the data, we should...",
                    "My recommendation is to...",
                    "I believe we need to..."
                ]
            },
            AuthorityLevel.ORDER: {
                "language_style": "directive",
                "autonomy_level": 0.2,
                "compliance_expectation": 0.95,
                "response_required": True,
                "phrases": [
                    "Please ensure that...",
                    "You need to...",
                    "It's critical that you...",
                    "I'm directing you to..."
                ]
            }
        }
        
        self.catch_ball_phases = [
            "initial_proposal",
            "clarification_request", 
            "refined_proposal",
            "pushback_concerns",
            "compromise_solution",
            "final_agreement"
        ]
        
        self.gossip_network_roles = {
            "influencer": ["VP Engineering", "VP Sales", "VP Marketing"],
            "connector": ["Engineering Manager", "Sales Manager", "Project Manager"],
            "informant": ["Senior Developer", "Account Manager", "HR Specialist"],
            "amplifier": ["Team Lead", "Department Head", "Practice Leader"]
        }

    def generate_enhanced_delegation_flow(self, org_data: Dict, scenario: Dict) -> Dict:
        """Generate delegation flow with authority levels and catch-ball patterns."""
        
        base_flow = self._generate_base_hierarchical_flow(org_data, scenario)
        
        # Add authority levels to each hierarchical step
        enhanced_flow = self._add_authority_levels(base_flow, org_data)
        
        # Generate catch-ball refinement cycles
        catch_ball_flows = self._generate_catch_ball_flows(enhanced_flow, org_data)
        
        # Generate gossip/wisdom-of-the-crowd flows
        gossip_flows = self._generate_gossip_flows(enhanced_flow, org_data, scenario)
        
        return {
            "scenario_id": f"{org_data['id']}_{scenario['type']}_enhanced",
            "organization_id": org_data['id'],
            "scenario_type": scenario['type'],
            "communication_patterns": {
                "hierarchical_delegation": enhanced_flow,
                "catch_ball_refinement": catch_ball_flows,
                "wisdom_of_the_crowd": gossip_flows
            },
            "flow_metadata": {
                "total_participants": len(self._get_all_participants(enhanced_flow, catch_ball_flows, gossip_flows)),
                "communication_cycles": len(catch_ball_flows),
                "gossip_threads": len(gossip_flows),
                "authority_distribution": self._analyze_authority_distribution(enhanced_flow)
            },
            "generated_at": datetime.now().isoformat()
        }

    def _add_authority_levels(self, base_flow: Dict, org_data: Dict) -> Dict:
        """Add authority levels to hierarchical delegation steps."""
        
        enhanced_steps = []
        
        for step in base_flow['flow_steps']:
            # Determine authority level based on roles and scenario urgency
            authority_level = self._determine_authority_level(
                step['from_role'], 
                step['to_role'], 
                base_flow.get('urgency_level', 'medium'),
                org_data
            )
            
            authority_data = self.authority_patterns[authority_level]
            
            enhanced_step = {
                **step,
                "authority_level": authority_level.value,
                "authority_metadata": {
                    "language_style": authority_data["language_style"],
                    "autonomy_level": authority_data["autonomy_level"],
                    "compliance_expectation": authority_data["compliance_expectation"],
                    "response_required": authority_data["response_required"]
                },
                "enhanced_message": self._craft_authority_message(
                    step['message'], 
                    authority_level,
                    step['from_role'],
                    step['to_role']
                ),
                "expected_recipient_response": self._generate_recipient_response(
                    authority_level, 
                    step['to_role'],
                    org_data
                )
            }
            
            enhanced_steps.append(enhanced_step)
        
        return {
            **base_flow,
            "flow_steps": enhanced_steps,
            "authority_analysis": self._analyze_authority_usage(enhanced_steps)
        }

    def _generate_catch_ball_flows(self, hierarchical_flow: Dict, org_data: Dict) -> List[Dict]:
        """Generate catch-ball style back-and-forth communication cycles."""
        
        catch_ball_cycles = []
        
        # Select key decision points for catch-ball refinement
        decision_steps = [step for step in hierarchical_flow['flow_steps'] 
                         if step.get('authority_level') in ['recommend', 'nudge']]
        
        for step in decision_steps[:2]:  # Limit to 2 catch-ball cycles per flow
            cycle = self._create_catch_ball_cycle(step, org_data)
            catch_ball_cycles.append(cycle)
        
        return catch_ball_cycles

    def _create_catch_ball_cycle(self, initial_step: Dict, org_data: Dict) -> Dict:
        """Create a complete catch-ball refinement cycle."""
        
        phases = []
        participants = [initial_step['from_role'], initial_step['to_role']]
        
        # Phase 1: Initial Proposal (from hierarchical flow)
        phases.append({
            "phase": "initial_proposal",
            "from_role": initial_step['from_role'],
            "to_role": initial_step['to_role'],
            "message": initial_step['enhanced_message'],
            "timestamp_offset": "0 minutes"
        })
        
        # Phase 2: Clarification Request
        phases.append({
            "phase": "clarification_request", 
            "from_role": initial_step['to_role'],
            "to_role": initial_step['from_role'],
            "message": self._generate_clarification_request(initial_step, org_data),
            "timestamp_offset": "45 minutes"
        })
        
        # Phase 3: Refined Proposal
        phases.append({
            "phase": "refined_proposal",
            "from_role": initial_step['from_role'],
            "to_role": initial_step['to_role'],
            "message": self._generate_refined_proposal(initial_step, org_data),
            "timestamp_offset": "2 hours"
        })
        
        # Phase 4: Concerns/Pushback (optional, based on org culture)
        if org_data.get('delegation_culture') == 'collaborative':
            phases.append({
                "phase": "pushback_concerns",
                "from_role": initial_step['to_role'],
                "to_role": initial_step['from_role'], 
                "message": self._generate_pushback_concerns(initial_step, org_data),
                "timestamp_offset": "3.5 hours"
            })
            
            # Phase 5: Compromise Solution
            phases.append({
                "phase": "compromise_solution",
                "from_role": initial_step['from_role'],
                "to_role": initial_step['to_role'],
                "message": self._generate_compromise_solution(initial_step, org_data),
                "timestamp_offset": "5 hours"
            })
        
        # Final Phase: Agreement
        phases.append({
            "phase": "final_agreement",
            "from_role": initial_step['to_role'],
            "to_role": initial_step['from_role'],
            "message": self._generate_final_agreement(initial_step, org_data),
            "timestamp_offset": "6 hours"
        })
        
        return {
            "cycle_id": f"catch_ball_{initial_step['from_role']}_{initial_step['to_role']}",
            "participants": participants,
            "total_phases": len(phases),
            "phases": phases,
            "outcome": "refined_mutual_understanding",
            "collaboration_score": 0.8 if org_data.get('delegation_culture') == 'collaborative' else 0.6
        }

    def _generate_gossip_flows(self, hierarchical_flow: Dict, org_data: Dict, scenario: Dict) -> List[Dict]:
        """Generate wisdom-of-the-crowd lateral communication patterns."""
        
        gossip_threads = []
        
        # Identify key information that would spread through gossip
        gossip_worthy_info = self._identify_gossip_triggers(hierarchical_flow, scenario)
        
        for info_item in gossip_worthy_info:
            thread = self._create_gossip_thread(info_item, org_data)
            gossip_threads.append(thread)
        
        return gossip_threads

    def _create_gossip_thread(self, info_item: Dict, org_data: Dict) -> Dict:
        """Create a single gossip communication thread."""
        
        # Select gossip network participants
        influencers = random.sample(self.gossip_network_roles['influencer'], 
                                  min(2, len(self.gossip_network_roles['influencer'])))
        connectors = random.sample(self.gossip_network_roles['connector'],
                                 min(3, len(self.gossip_network_roles['connector'])))
        informants = random.sample(self.gossip_network_roles['informant'],
                                 min(2, len(self.gossip_network_roles['informant'])))
        
        gossip_steps = []
        
        # Step 1: Influencer shares initial insight
        gossip_steps.append({
            "step": 1,
            "communication_type": "initial_insight",
            "from_role": influencers[0],
            "to_roles": connectors[:2],
            "channel": "coffee_chat",
            "message": self._generate_gossip_message(info_item, "initial_insight"),
            "confidence_level": 0.7,
            "information_mutation": 0.1  # How much info changes
        })
        
        # Step 2: Connectors amplify and interpret
        for i, connector in enumerate(connectors[:2]):
            gossip_steps.append({
                "step": 2 + i,
                "communication_type": "amplification",
                "from_role": connector,
                "to_roles": [connectors[2], informants[0]],
                "channel": random.choice(["slack_dm", "hallway_conversation", "lunch_discussion"]),
                "message": self._generate_gossip_message(info_item, "amplification"),
                "confidence_level": 0.6,
                "information_mutation": 0.2
            })
        
        # Step 3: Informants add context and spread further
        gossip_steps.append({
            "step": len(gossip_steps) + 1,
            "communication_type": "contextualization",
            "from_role": informants[0],
            "to_roles": [informants[1], "Team Members"],
            "channel": "team_channel",
            "message": self._generate_gossip_message(info_item, "contextualization"),
            "confidence_level": 0.5,
            "information_mutation": 0.3
        })
        
        # Step 4: Wisdom emerges from collective interpretation
        gossip_steps.append({
            "step": len(gossip_steps) + 1,
            "communication_type": "collective_wisdom",
            "from_role": "Team Members",
            "to_roles": ["Department"],
            "channel": "team_meeting",
            "message": self._generate_collective_wisdom(info_item, org_data),
            "confidence_level": 0.8,
            "information_mutation": 0.1,
            "wisdom_quality": "enhanced_understanding"
        })
        
        return {
            "thread_id": f"gossip_{info_item['topic']}_thread",
            "trigger_info": info_item,
            "network_reach": len(set([step.get('from_role') for step in gossip_steps] + 
                                   [role for step in gossip_steps for role in step.get('to_roles', [])])),
            "steps": gossip_steps,
            "final_sentiment": self._analyze_gossip_sentiment(gossip_steps),
            "information_drift": self._calculate_information_drift(gossip_steps),
            "collective_insight": self._extract_collective_insight(gossip_steps, org_data)
        }

    def _determine_authority_level(self, from_role: str, to_role: str, urgency: str, org_data: Dict) -> AuthorityLevel:
        """Determine appropriate authority level based on context."""
        
        # Role hierarchy mapping
        hierarchy_levels = {
            "CEO": 1, "COO": 2, "CTO": 2, "CFO": 2,
            "VP Engineering": 3, "VP Sales": 3, "VP Marketing": 3,
            "Engineering Manager": 4, "Sales Manager": 4,
            "Senior Developer": 5, "Account Manager": 5
        }
        
        from_level = hierarchy_levels.get(from_role, 3)
        to_level = hierarchy_levels.get(to_role, 4)
        level_gap = to_level - from_level
        
        # Organizational culture influence
        culture = org_data.get('delegation_culture', 'hierarchical')
        
        # Decision logic
        if urgency == 'critical' or level_gap >= 3:
            return AuthorityLevel.ORDER
        elif urgency == 'high' or (level_gap >= 2 and culture == 'hierarchical'):
            return AuthorityLevel.RECOMMEND
        elif culture == 'collaborative' or level_gap == 1:
            return AuthorityLevel.NUDGE
        else:
            return AuthorityLevel.RECOMMEND

    def _craft_authority_message(self, base_message: str, authority_level: AuthorityLevel, 
                                from_role: str, to_role: str) -> str:
        """Craft message with appropriate authority level language."""
        
        phrases = self.authority_patterns[authority_level]["phrases"]
        selected_phrase = random.choice(phrases)
        
        return f"{selected_phrase} {base_message.lower()}"

    def _generate_recipient_response(self, authority_level: AuthorityLevel, 
                                   recipient_role: str, org_data: Dict) -> Dict:
        """Generate expected response based on authority level and org culture."""
        
        culture = org_data.get('delegation_culture', 'hierarchical')
        
        response_patterns = {
            AuthorityLevel.NUDGE: {
                "collaborative": "Thanks for the suggestion. Let me explore this and get back to you with my thoughts.",
                "hierarchical": "I'll consider this approach and update you on my decision."
            },
            AuthorityLevel.RECOMMEND: {
                "collaborative": "I understand the recommendation. Can we discuss the implementation details?",
                "hierarchical": "Understood. I'll proceed with your recommendation and provide status updates."
            },
            AuthorityLevel.ORDER: {
                "collaborative": "Acknowledged. I'll execute this immediately and confirm completion.",
                "hierarchical": "Yes, will complete as directed and report back."
            }
        }
        
        return {
            "expected_response": response_patterns[authority_level][culture],
            "response_time": "within 2 hours" if authority_level == AuthorityLevel.ORDER else "within 24 hours",
            "follow_up_required": authority_level in [AuthorityLevel.RECOMMEND, AuthorityLevel.ORDER]
        }

    # Helper methods for generating specific communication content
    def _generate_clarification_request(self, step: Dict, org_data: Dict) -> str:
        return f"I want to make sure I understand correctly. When you say '{step['message'][:30]}...', are you thinking we should prioritize X or Y approach?"

    def _generate_refined_proposal(self, step: Dict, org_data: Dict) -> str:
        return f"Good point. Let me refine the approach: {step['message']} But let's also consider the resource implications and timeline constraints."

    def _generate_pushback_concerns(self, step: Dict, org_data: Dict) -> str:
        return f"I see the value in this direction, but I have concerns about feasibility given our current capacity. What if we tried a phased approach instead?"

    def _generate_compromise_solution(self, step: Dict, org_data: Dict) -> str:
        return "You raise valid concerns. How about we pilot this with a smaller scope first, then scale based on results?"

    def _generate_final_agreement(self, step: Dict, org_data: Dict) -> str:
        return "That works well. I'm comfortable with this refined approach. Let's move forward and I'll keep you updated on progress."

    def _identify_gossip_triggers(self, hierarchical_flow: Dict, scenario: Dict) -> List[Dict]:
        """Identify information that would spread through informal networks."""
        return [
            {
                "topic": "budget_concerns",
                "trigger": "CFO mentioned resource constraints",
                "interest_level": 0.8
            },
            {
                "topic": "leadership_change",
                "trigger": "Unusual meeting patterns observed",
                "interest_level": 0.9
            }
        ]

    def _generate_gossip_message(self, info_item: Dict, message_type: str) -> str:
        messages = {
            "initial_insight": f"Did you hear about the {info_item['topic']}? I think there might be bigger changes coming...",
            "amplification": f"Yeah, I heard something similar about {info_item['topic']}. Makes you wonder about our department's priorities...",
            "contextualization": f"This {info_item['topic']} situation actually connects to what we saw last quarter. The team has some ideas about how to handle it..."
        }
        return messages.get(message_type, f"There's some interesting discussion about {info_item['topic']}")

    def _generate_collective_wisdom(self, info_item: Dict, org_data: Dict) -> str:
        return f"After discussing {info_item['topic']} across the team, we think the real issue is about resource allocation and communication. Here's what we've learned..."

    def _analyze_gossip_sentiment(self, steps: List[Dict]) -> str:
        return random.choice(["constructive", "concerned", "optimistic", "cautious"])

    def _calculate_information_drift(self, steps: List[Dict]) -> float:
        return sum([step.get('information_mutation', 0) for step in steps]) / len(steps)

    def _extract_collective_insight(self, steps: List[Dict], org_data: Dict) -> str:
        return "Team has developed nuanced understanding of the situation with practical implementation ideas."

    # Base flow generation methods (simplified versions of previous implementation)
    def _generate_base_hierarchical_flow(self, org_data: Dict, scenario: Dict) -> Dict:
        """Generate basic hierarchical delegation flow."""
        return {
            "flow_steps": [
                {
                    "from_role": "CEO",
                    "to_role": "CFO", 
                    "message": scenario.get('trigger', 'Handle this situation'),
                    "step_number": 1
                },
                {
                    "from_role": "CFO",
                    "to_role": "VP Sales",
                    "message": "Need analysis for the CEO's request",
                    "step_number": 2
                }
            ],
            "urgency_level": scenario.get('urgency', 'medium')
        }

    def _get_all_participants(self, hierarchical: Dict, catch_ball: List[Dict], gossip: List[Dict]) -> List[str]:
        """Get all unique participants across communication flows."""
        participants = set()
        
        # From hierarchical flow
        for step in hierarchical.get('flow_steps', []):
            participants.add(step.get('from_role'))
            participants.add(step.get('to_role'))
        
        # From catch-ball flows
        for cycle in catch_ball:
            participants.update(cycle.get('participants', []))
        
        # From gossip flows  
        for thread in gossip:
            for step in thread.get('steps', []):
                participants.add(step.get('from_role'))
                participants.update(step.get('to_roles', []))
        
        return list(participants)

    def _analyze_authority_distribution(self, flow: Dict) -> Dict:
        """Analyze the distribution of authority levels in the flow."""
        levels = [step.get('authority_level') for step in flow.get('flow_steps', [])]
        return {
            "nudge_count": levels.count('nudge'),
            "recommend_count": levels.count('recommend'), 
            "order_count": levels.count('order'),
            "authority_balance": "collaborative" if levels.count('nudge') > levels.count('order') else "directive"
        }

    def _analyze_authority_usage(self, steps: List[Dict]) -> Dict:
        """Analyze how authority is used across the delegation flow."""
        return {
            "predominant_style": "collaborative",  # Based on authority distribution
            "escalation_points": 2,  # Points where authority level increases
            "collaboration_opportunities": 3  # Catch-ball potential points
        }


def enhance_existing_flows_with_advanced_communication():
    """Enhance existing flows with new communication patterns."""
    
    generator = EnhancedCommunicationFlow()
    base_path = Path("/Users/kenper/src/aprio-one/tech-europe-hackathon/living-twin-synthetic-data")
    orgs_path = base_path / "generated" / "structured" / "organizations"
    
    # Process first enhanced organization as example
    org_dir = orgs_path / "org_000"
    flows_dir = org_dir / "flows"
    
    if not flows_dir.exists():
        print(f"No flows directory found for {org_dir.name}")
        return
    
    # Read organization data
    org_json = org_dir / f"{org_dir.name}.json"
    with open(org_json, 'r') as f:
        org_data = json.load(f)
    
    print(f"Enhancing {org_data['name']} with advanced communication patterns...")
    
    # Process existing scenarios
    for flow_file in flows_dir.glob("*.json"):
        if "enhanced" in flow_file.name:
            continue  # Skip already enhanced flows
            
        with open(flow_file, 'r') as f:
            existing_flow = json.load(f)
        
        scenario = {
            "type": existing_flow["scenario_type"],
            "trigger": existing_flow["trigger"],
            "urgency": existing_flow["urgency_level"]
        }
        
        # Generate enhanced communication flow
        enhanced_flow = generator.generate_enhanced_delegation_flow(org_data, scenario)
        
        # Save enhanced flow
        enhanced_file = flows_dir / f"{flow_file.stem}_enhanced.json"
        with open(enhanced_file, 'w') as f:
            json.dump(enhanced_flow, f, indent=2)
        
        # Generate readable markdown
        enhanced_md = flows_dir / f"{flow_file.stem}_enhanced.md"
        generate_enhanced_flow_markdown(enhanced_flow, enhanced_md)
        
        print(f"  ✓ Enhanced {flow_file.stem} with authority levels, catch-ball, and gossip flows")

def generate_enhanced_flow_markdown(flow_data: Dict, output_file: Path):
    """Generate markdown for enhanced communication flows."""
    
    content = f"""# Enhanced Communication Flow: {flow_data['scenario_type'].title().replace('_', ' ')}

## Scenario Overview
- **Organization**: {flow_data['organization_id']}  
- **Total Participants**: {flow_data['flow_metadata']['total_participants']}
- **Communication Cycles**: {flow_data['flow_metadata']['communication_cycles']}
- **Gossip Threads**: {flow_data['flow_metadata']['gossip_threads']}

## 1. Hierarchical Delegation (Authority-Based)

"""
    
    for step in flow_data['communication_patterns']['hierarchical_delegation']['flow_steps']:
        authority_level = step['authority_level'].upper()
        content += f"""### {step['from_role']} → {step['to_role']} [{authority_level}]

**Enhanced Message**: {step['enhanced_message']}

**Authority Context**:
- Language Style: {step['authority_metadata']['language_style']}
- Autonomy Level: {step['authority_metadata']['autonomy_level']:.1f}
- Compliance Expected: {step['authority_metadata']['compliance_expectation']:.1f}

**Expected Response**: {step['expected_recipient_response']['expected_response']}

---

"""
    
    # Catch-ball flows section
    content += "\n## 2. Catch-Ball Refinement Cycles\n\n"
    
    for cycle in flow_data['communication_patterns']['catch_ball_refinement']:
        content += f"""### {cycle['cycle_id']}
**Participants**: {', '.join(cycle['participants'])}
**Collaboration Score**: {cycle['collaboration_score']}

"""
        for phase in cycle['phases']:
            content += f"**{phase['phase'].title()}** ({phase['timestamp_offset']}): {phase['message']}\n\n"
    
    # Gossip flows section
    content += "\n## 3. Wisdom-of-the-Crowd (Gossip Network)\n\n"
    
    for thread in flow_data['communication_patterns']['wisdom_of_the_crowd']:
        content += f"""### {thread['thread_id']}
**Network Reach**: {thread['network_reach']} people
**Information Drift**: {thread['information_drift']:.2f}
**Final Sentiment**: {thread['final_sentiment']}

**Collective Insight**: {thread['collective_insight']}

"""
        for step in thread['steps']:
            content += f"**Step {step['step']}** ({step['communication_type']}): {step['from_role']} → {', '.join(step.get('to_roles', []))} via {step['channel']}\n"
            content += f"Message: {step['message']}\n\n"
    
    content += f"""
## Communication Analysis

**Authority Distribution**: {flow_data['flow_metadata']['authority_distribution']}

This enhanced flow demonstrates:
1. **Authority Levels**: Appropriate use of nudge/recommend/order based on hierarchy and culture
2. **Catch-Ball Refinement**: Collaborative back-and-forth for complex decisions  
3. **Wisdom-of-the-Crowd**: How information spreads and evolves through informal networks

*Generated by Living Twin Enhanced Communication System*
"""
    
    with open(output_file, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    enhance_existing_flows_with_advanced_communication()
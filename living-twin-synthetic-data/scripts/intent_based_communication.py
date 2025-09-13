#!/usr/bin/env python3
"""
Intent-Based Communication System
Focuses on meaning, expectation, intent, and certainty rather than just message passing.
Includes sender-receiver relationship context and intelligent message interpretation.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass

class MessageIntent(Enum):
    """Core intent categories for organizational communication."""
    INFORMATION_SHARING = "information_sharing"    # FYI, context building
    DECISION_REQUEST = "decision_request"          # Need approval/choice
    ACTION_DIRECTIVE = "action_directive"         # Must execute
    OPINION_SEEKING = "opinion_seeking"           # Want input/advice  
    STATUS_UPDATE = "status_update"               # Progress report
    PROBLEM_ESCALATION = "problem_escalation"     # Issue needs attention
    RESOURCE_REQUEST = "resource_request"         # Need people/budget/time
    RELATIONSHIP_BUILDING = "relationship_building" # Trust/rapport development

class CertaintyLevel(Enum):
    """Sender's confidence in their message content."""
    ABSOLUTE = "absolute"        # 95-100% certain
    HIGH = "high"               # 80-94% certain
    MODERATE = "moderate"       # 60-79% certain
    LOW = "low"                 # 40-59% certain
    SPECULATIVE = "speculative" # <40% certain

class ExecutionExpectation(Enum):
    """What sender expects recipient to do."""
    IMMEDIATE_ACTION = "immediate_action"       # Within hours
    PLANNED_EXECUTION = "planned_execution"     # Within days/weeks
    CONSIDERATION = "consideration"             # Think about it
    AWARENESS_ONLY = "awareness_only"          # Just know this
    FEEDBACK_REQUIRED = "feedback_required"    # Need response
    COLLABORATION_NEEDED = "collaboration_needed" # Work together

@dataclass
class SenderProfile:
    """Rich context about the message sender based on organizational history."""
    role: str
    communication_style: str    # direct, diplomatic, analytical, emotional
    reliability_score: float    # 0-1, based on past follow-through
    expertise_domains: List[str] # Areas of known competence
    decision_authority_level: int # 1-10 organizational authority
    typical_urgency_calibration: float # How well they judge urgency (0-1)
    trust_level_with_recipient: float # Relationship-specific trust (0-1)
    historical_intent_accuracy: float # How often their stated intent matches reality
    stress_indicators: Dict[str, float] # Current stress levels affecting communication
    recent_context: List[str] # Recent events affecting their perspective

@dataclass
class RecipientProfile:
    """Context about message recipient for interpretation."""
    role: str
    processing_style: str       # analytical, intuitive, collaborative, decisive
    autonomy_preference: float  # 0-1, how much independence they want
    expertise_domains: List[str]
    current_workload: float     # 0-1, affects response capacity
    relationship_with_sender: str # peer, subordinate, superior, cross-functional
    historical_response_patterns: Dict[str, float] # How they typically respond to different intents
    trust_level_with_sender: float
    current_priorities: List[str] # What they're focused on right now
    decision_making_speed: str  # fast, moderate, deliberate
    decision_authority_level: int # 1-10 organizational authority

class IntentBasedMessage:
    """Enhanced message with rich contextual metadata."""
    
    def __init__(self, sender_profile: SenderProfile, recipient_profile: RecipientProfile):
        self.sender = sender_profile
        self.recipient = recipient_profile
        
    def create_message(self, content: str, scenario_context: Dict) -> Dict:
        """Create message with full intent-based metadata."""
        
        # Analyze message intent based on content and context
        primary_intent = self._determine_primary_intent(content, scenario_context)
        secondary_intents = self._identify_secondary_intents(content, scenario_context)
        
        # Assess sender's certainty based on their profile and content
        certainty_level = self._assess_certainty_level(content, scenario_context)
        
        # Determine execution expectations
        execution_expectation = self._determine_execution_expectation(
            primary_intent, scenario_context, self.sender, self.recipient
        )
        
        # Generate sender attribution metadata
        sender_attribution = self._generate_sender_attribution()
        
        # Generate recipient interpretation and recommendations
        recipient_interpretation = self._generate_recipient_interpretation(
            primary_intent, certainty_level, execution_expectation
        )
        
        return {
            "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            "timestamp": datetime.now().isoformat(),
            
            # Core message content
            "raw_content": content,
            "processed_content": self._enhance_content_with_context(content, primary_intent),
            
            # Intent analysis
            "intent_analysis": {
                "primary_intent": primary_intent.value,
                "secondary_intents": [intent.value for intent in secondary_intents],
                "intent_confidence": self._calculate_intent_confidence(),
                "decision_type": self._classify_decision_type(primary_intent, scenario_context)
            },
            
            # Certainty and expectations
            "certainty_metadata": {
                "sender_certainty_level": certainty_level.value,
                "certainty_indicators": self._identify_certainty_indicators(content),
                "information_completeness": self._assess_information_completeness(content, scenario_context),
                "assumption_dependencies": self._identify_assumptions(content)
            },
            
            "execution_metadata": {
                "execution_expectation": execution_expectation.value,
                "urgency_level": self._determine_urgency(scenario_context, self.sender),
                "success_criteria": self._define_success_criteria(primary_intent, content),
                "resource_requirements": self._estimate_resource_requirements(content, execution_expectation),
                "timeline_expectations": self._estimate_timeline_expectations(execution_expectation)
            },
            
            # Sender context and attribution
            "sender_attribution": sender_attribution,
            
            # Recipient interpretation and recommendations
            "recipient_guidance": recipient_interpretation,
            
            # Relationship dynamics
            "relationship_context": self._analyze_relationship_dynamics(),
            
            # Message evolution tracking
            "evolution_metadata": {
                "message_generation": 1,  # For catch-ball tracking
                "parent_message_id": None,
                "evolution_type": "original",  # original, clarification, refinement, response
                "cumulative_context": [content]
            }
        }
    
    def _determine_primary_intent(self, content: str, scenario_context: Dict) -> MessageIntent:
        """Analyze content and context to determine primary intent."""
        
        # Keyword-based intent detection (simplified for demo)
        decision_keywords = ["approve", "decide", "choose", "select", "authorize"]
        action_keywords = ["execute", "implement", "complete", "deliver", "ensure"]
        info_keywords = ["fyi", "update", "inform", "awareness", "context"]
        opinion_keywords = ["think", "recommend", "suggest", "advise", "opinion"]
        
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in decision_keywords):
            return MessageIntent.DECISION_REQUEST
        elif any(keyword in content_lower for keyword in action_keywords):
            return MessageIntent.ACTION_DIRECTIVE
        elif any(keyword in content_lower for keyword in info_keywords):
            return MessageIntent.INFORMATION_SHARING
        elif any(keyword in content_lower for keyword in opinion_keywords):
            return MessageIntent.OPINION_SEEKING
        elif scenario_context.get('urgency') == 'critical':
            return MessageIntent.PROBLEM_ESCALATION
        else:
            # Default based on relationship and authority
            if self.sender.decision_authority_level > self.recipient.decision_authority_level + 2:
                return MessageIntent.ACTION_DIRECTIVE
            else:
                return MessageIntent.INFORMATION_SHARING
    
    def _identify_secondary_intents(self, content: str, scenario_context: Dict) -> List[MessageIntent]:
        """Identify additional intents in the message."""
        secondary = []
        
        # Most messages have relationship-building undertones
        if self.sender.trust_level_with_recipient < 0.7:
            secondary.append(MessageIntent.RELATIONSHIP_BUILDING)
        
        # Resource implications often embedded in other intents
        if any(word in content.lower() for word in ["budget", "resources", "people", "time"]):
            secondary.append(MessageIntent.RESOURCE_REQUEST)
        
        return secondary
    
    def _assess_certainty_level(self, content: str, scenario_context: Dict) -> CertaintyLevel:
        """Assess sender's certainty based on language and context."""
        
        # Language indicators
        certainty_indicators = {
            "absolute": ["definitely", "certainly", "absolutely", "guaranteed", "confirmed"],
            "high": ["confident", "likely", "should", "expect", "probable"],
            "moderate": ["believe", "think", "seems", "appears", "probably"],
            "low": ["might", "could", "possibly", "uncertain", "unclear"],
            "speculative": ["maybe", "perhaps", "speculation", "guess", "wondering"]
        }
        
        content_lower = content.lower()
        
        for level, keywords in certainty_indicators.items():
            if any(keyword in content_lower for keyword in keywords):
                return CertaintyLevel(level)
        
        # Default based on sender's typical confidence and scenario
        if scenario_context.get('urgency') == 'critical':
            return CertaintyLevel.HIGH  # Crisis demands decisiveness
        elif self.sender.typical_urgency_calibration > 0.8:
            return CertaintyLevel.HIGH
        else:
            return CertaintyLevel.MODERATE
    
    def _determine_execution_expectation(self, intent: MessageIntent, scenario_context: Dict, 
                                       sender: SenderProfile, recipient: RecipientProfile) -> ExecutionExpectation:
        """Determine what sender expects recipient to do."""
        
        # Intent-based expectations
        intent_mapping = {
            MessageIntent.ACTION_DIRECTIVE: ExecutionExpectation.IMMEDIATE_ACTION if scenario_context.get('urgency') == 'critical' else ExecutionExpectation.PLANNED_EXECUTION,
            MessageIntent.DECISION_REQUEST: ExecutionExpectation.FEEDBACK_REQUIRED,
            MessageIntent.INFORMATION_SHARING: ExecutionExpectation.AWARENESS_ONLY,
            MessageIntent.OPINION_SEEKING: ExecutionExpectation.FEEDBACK_REQUIRED,
            MessageIntent.PROBLEM_ESCALATION: ExecutionExpectation.IMMEDIATE_ACTION,
            MessageIntent.RESOURCE_REQUEST: ExecutionExpectation.CONSIDERATION
        }
        
        base_expectation = intent_mapping.get(intent, ExecutionExpectation.CONSIDERATION)
        
        # Relationship-based adjustments
        if sender.decision_authority_level > recipient.decision_authority_level + 1:
            # Higher authority expects more execution
            if base_expectation == ExecutionExpectation.CONSIDERATION:
                return ExecutionExpectation.PLANNED_EXECUTION
            elif base_expectation == ExecutionExpectation.AWARENESS_ONLY:
                return ExecutionExpectation.CONSIDERATION
        
        return base_expectation
    
    def _generate_sender_attribution(self) -> Dict:
        """Generate rich metadata about the sender's context and history."""
        
        return {
            "sender_context": {
                "role": self.sender.role,
                "communication_style": self.sender.communication_style,
                "reliability_score": self.sender.reliability_score,
                "expertise_match": self._calculate_expertise_match(),
                "authority_level": self.sender.decision_authority_level,
                "urgency_calibration": self.sender.typical_urgency_calibration
            },
            
            "historical_patterns": {
                "intent_accuracy": self.sender.historical_intent_accuracy,
                "follow_through_rate": self.sender.reliability_score,
                "typical_response_time": self._estimate_sender_typical_response_time(),
                "escalation_tendencies": self._analyze_escalation_patterns()
            },
            
            "current_state": {
                "stress_level": self.sender.stress_indicators.get('overall', 0.3),
                "workload_pressure": self.sender.stress_indicators.get('workload', 0.4),
                "recent_context_influence": self._assess_recent_context_influence(),
                "relationship_quality": self.sender.trust_level_with_recipient
            },
            
            "interpretation_guidance": {
                "communication_style_notes": self._generate_style_guidance(),
                "reliability_context": self._generate_reliability_context(),
                "expertise_trust_level": self._calculate_expertise_trust()
            }
        }
    
    def _generate_recipient_interpretation(self, intent: MessageIntent, 
                                         certainty: CertaintyLevel, 
                                         execution_expectation: ExecutionExpectation) -> Dict:
        """Generate interpretation guidance and recommendations for recipient."""
        
        return {
            "interpretation_analysis": {
                "suggested_interpretation": self._generate_interpretation_suggestion(intent, certainty),
                "confidence_in_interpretation": self._calculate_interpretation_confidence(),
                "alternative_interpretations": self._generate_alternative_interpretations(intent),
                "context_dependencies": self._identify_context_dependencies()
            },
            
            "response_recommendations": {
                "recommended_response_type": self._recommend_response_type(intent, execution_expectation),
                "response_urgency": self._calculate_recommended_response_urgency(),
                "key_points_to_address": self._identify_key_response_points(intent),
                "relationship_considerations": self._generate_relationship_guidance()
            },
            
            "execution_guidance": {
                "immediate_actions": self._recommend_immediate_actions(execution_expectation),
                "decision_points": self._identify_decision_points(intent),
                "resource_implications": self._analyze_resource_implications(),
                "success_indicators": self._define_success_indicators(intent, execution_expectation),
                "risk_factors": self._identify_risk_factors()
            },
            
            "escalation_guidance": {
                "escalation_triggers": self._define_escalation_triggers(),
                "escalation_path": self._recommend_escalation_path(),
                "stakeholders_to_involve": self._identify_key_stakeholders()
            }
        }
    
    def create_response_message(self, original_message: Dict, response_content: str, 
                              response_type: str = "standard") -> Dict:
        """Create a response message with evolved context."""
        
        # Swap sender/recipient for response
        response_message = IntentBasedMessage(
            sender_profile=self.recipient,
            recipient_profile=self.sender
        )
        
        # Create response with evolved context
        scenario_context = {"urgency": "medium", "type": "response"}
        response_msg = response_message.create_message(response_content, scenario_context)
        
        # Link to original message
        response_msg["evolution_metadata"].update({
            "message_generation": original_message["evolution_metadata"]["message_generation"] + 1,
            "parent_message_id": original_message["message_id"],
            "evolution_type": response_type,
            "cumulative_context": original_message["evolution_metadata"]["cumulative_context"] + [response_content]
        })
        
        return response_msg
    
    # Helper methods for various calculations and analyses
    def _enhance_content_with_context(self, content: str, intent: MessageIntent) -> str:
        """Enhance raw content with contextual understanding."""
        return f"[{intent.value.upper()}] {content}"
    
    def _calculate_intent_confidence(self) -> float:
        """Calculate confidence in intent detection."""
        return 0.85  # Simplified for demo
    
    def _classify_decision_type(self, intent: MessageIntent, scenario_context: Dict) -> str:
        """Classify the type of decision if applicable."""
        if intent == MessageIntent.DECISION_REQUEST:
            return "operational_decision"
        elif intent == MessageIntent.PROBLEM_ESCALATION:
            return "crisis_decision"
        else:
            return "no_decision_required"
    
    def _identify_certainty_indicators(self, content: str) -> List[str]:
        """Identify words/phrases that indicate certainty level."""
        indicators = []
        certainty_words = ["definitely", "probably", "might", "certainly", "unclear"]
        for word in certainty_words:
            if word in content.lower():
                indicators.append(word)
        return indicators
    
    def _assess_information_completeness(self, content: str, scenario_context: Dict) -> float:
        """Assess how complete the information is."""
        return 0.75  # Simplified calculation
    
    def _identify_assumptions(self, content: str) -> List[str]:
        """Identify assumptions embedded in the message."""
        return ["Budget approval assumed", "Timeline feasibility assumed"]  # Example
    
    def _determine_urgency(self, scenario_context: Dict, sender: SenderProfile) -> str:
        """Determine message urgency considering sender calibration."""
        base_urgency = scenario_context.get('urgency', 'medium')
        
        # Adjust based on sender's urgency calibration
        if sender.typical_urgency_calibration < 0.5:  # Under-estimates urgency
            urgency_map = {"low": "low", "medium": "low", "high": "medium", "critical": "high"}
            return urgency_map.get(base_urgency, base_urgency)
        elif sender.typical_urgency_calibration > 0.8:  # Over-estimates urgency
            urgency_map = {"low": "medium", "medium": "high", "high": "critical", "critical": "critical"}
            return urgency_map.get(base_urgency, base_urgency)
        
        return base_urgency
    
    def _define_success_criteria(self, intent: MessageIntent, content: str) -> List[str]:
        """Define what success looks like for this message."""
        criteria_map = {
            MessageIntent.ACTION_DIRECTIVE: ["Task completed on time", "Quality standards met"],
            MessageIntent.DECISION_REQUEST: ["Decision made with rationale", "Stakeholders informed"],
            MessageIntent.INFORMATION_SHARING: ["Information acknowledged", "Relevant questions asked"],
            MessageIntent.OPINION_SEEKING: ["Thoughtful input provided", "Perspective shared"]
        }
        return criteria_map.get(intent, ["Message acknowledged"])
    
    def _estimate_resource_requirements(self, content: str, execution_expectation: ExecutionExpectation) -> Dict:
        """Estimate resources needed to fulfill the message."""
        if execution_expectation == ExecutionExpectation.IMMEDIATE_ACTION:
            return {"time": "2-4 hours", "people": "1-2", "budget": "minimal"}
        elif execution_expectation == ExecutionExpectation.PLANNED_EXECUTION:
            return {"time": "1-3 days", "people": "2-5", "budget": "moderate"}
        else:
            return {"time": "30 minutes", "people": "1", "budget": "none"}
    
    def _estimate_timeline_expectations(self, execution_expectation: ExecutionExpectation) -> str:
        """Estimate expected timeline based on execution expectation."""
        timeline_map = {
            ExecutionExpectation.IMMEDIATE_ACTION: "within 4 hours",
            ExecutionExpectation.PLANNED_EXECUTION: "within 1 week", 
            ExecutionExpectation.FEEDBACK_REQUIRED: "within 24 hours",
            ExecutionExpectation.CONSIDERATION: "within 2-3 days",
            ExecutionExpectation.AWARENESS_ONLY: "no timeline"
        }
        return timeline_map.get(execution_expectation, "within 24 hours")
    
    def _calculate_expertise_match(self) -> float:
        """Calculate how well sender's expertise matches the topic."""
        return 0.8  # Simplified
    
    def _estimate_sender_typical_response_time(self) -> str:
        """Estimate how quickly this sender typically responds."""
        if self.sender.communication_style == "direct":
            return "2-4 hours"
        else:
            return "4-8 hours"
    
    def _analyze_escalation_patterns(self) -> str:
        """Analyze sender's escalation tendencies."""
        return "moderate escalator"  # Simplified
    
    def _assess_recent_context_influence(self) -> float:
        """Assess how much recent events influence this message."""
        return len(self.sender.recent_context) * 0.1
    
    def _generate_style_guidance(self) -> str:
        """Generate guidance about sender's communication style."""
        style_guidance = {
            "direct": "Expects clear, concise responses. Values efficiency over diplomacy.",
            "diplomatic": "Appreciates thoughtful, nuanced responses. Considers relationship impact.",
            "analytical": "Wants data-driven responses with clear reasoning. Likes details.",
            "emotional": "Responds well to empathy and personal connection. Values team harmony."
        }
        return style_guidance.get(self.sender.communication_style, "Standard professional approach.")
    
    def _generate_reliability_context(self) -> str:
        """Generate context about sender's reliability."""
        if self.sender.reliability_score > 0.8:
            return "High reliability - commitments are typically fulfilled as promised."
        elif self.sender.reliability_score > 0.6:
            return "Moderate reliability - generally follows through but may need gentle reminders."
        else:
            return "Variable reliability - confirm understanding and establish checkpoints."
    
    def _calculate_expertise_trust(self) -> float:
        """Calculate trust level in sender's expertise for this topic."""
        return min(self.sender.reliability_score + 0.2, 1.0)
    
    def _generate_interpretation_suggestion(self, intent: MessageIntent, certainty: CertaintyLevel) -> str:
        """Generate suggested interpretation of the message."""
        return f"This appears to be {intent.value} with {certainty.value} certainty level from sender."
    
    def _calculate_interpretation_confidence(self) -> float:
        """Calculate confidence in the interpretation."""
        return 0.8  # Based on various factors
    
    def _generate_alternative_interpretations(self, intent: MessageIntent) -> List[str]:
        """Generate alternative ways to interpret the message."""
        return ["Could also be relationship building", "Might be testing waters for larger decision"]
    
    def _identify_context_dependencies(self) -> List[str]:
        """Identify what context is needed for full understanding."""
        return ["Previous project status", "Budget constraints", "Team capacity"]
    
    def _recommend_response_type(self, intent: MessageIntent, execution_expectation: ExecutionExpectation) -> str:
        """Recommend type of response."""
        if intent == MessageIntent.DECISION_REQUEST:
            return "decision_with_rationale"
        elif intent == MessageIntent.ACTION_DIRECTIVE:
            return "confirmation_with_timeline"
        else:
            return "acknowledgment_with_questions"
    
    def _calculate_recommended_response_urgency(self) -> str:
        """Calculate recommended response urgency."""
        return "within 24 hours"  # Based on various factors
    
    def _identify_key_response_points(self, intent: MessageIntent) -> List[str]:
        """Identify key points that should be addressed in response."""
        return ["Acknowledge understanding", "Clarify any ambiguities", "Confirm timeline"]
    
    def _generate_relationship_guidance(self) -> str:
        """Generate guidance for maintaining/building relationship."""
        return "Maintain professional tone while showing engagement with the request."
    
    def _recommend_immediate_actions(self, execution_expectation: ExecutionExpectation) -> List[str]:
        """Recommend immediate actions to take."""
        if execution_expectation == ExecutionExpectation.IMMEDIATE_ACTION:
            return ["Acknowledge receipt", "Begin preliminary work", "Identify resource needs"]
        else:
            return ["Acknowledge receipt", "Add to planning queue"]
    
    def _identify_decision_points(self, intent: MessageIntent) -> List[str]:
        """Identify key decision points."""
        return ["Resource allocation decision", "Timeline prioritization"]
    
    def _analyze_resource_implications(self) -> Dict:
        """Analyze resource implications."""
        return {"people": "2-3 team members", "time": "1-2 weeks", "budget": "moderate"}
    
    def _define_success_indicators(self, intent: MessageIntent, execution_expectation: ExecutionExpectation) -> List[str]:
        """Define success indicators."""
        return ["Stakeholder satisfaction", "On-time delivery", "Quality standards met"]
    
    def _identify_risk_factors(self) -> List[str]:
        """Identify potential risk factors."""
        return ["Resource conflicts", "Timeline constraints", "Dependency delays"]
    
    def _define_escalation_triggers(self) -> List[str]:
        """Define when to escalate."""
        return ["No progress after 48 hours", "Resource conflicts arise", "Quality concerns emerge"]
    
    def _recommend_escalation_path(self) -> str:
        """Recommend escalation path."""
        return f"First to {self.sender.role}, then to department head if unresolved"
    
    def _identify_key_stakeholders(self) -> List[str]:
        """Identify key stakeholders to involve."""
        return ["Project manager", "Resource owners", "End users"]
    
    def _analyze_relationship_dynamics(self) -> Dict:
        """Analyze sender-recipient relationship dynamics."""
        return {
            "relationship_type": self.recipient.relationship_with_sender,
            "trust_level": self.sender.trust_level_with_recipient,
            "power_dynamic": "peer" if abs(self.sender.decision_authority_level - self.recipient.decision_authority_level) <= 1 else "hierarchical",
            "collaboration_history": "positive" if self.sender.trust_level_with_recipient > 0.7 else "developing",
            "communication_compatibility": self._assess_communication_compatibility()
        }
    
    def _assess_communication_compatibility(self) -> str:
        """Assess how compatible sender and recipient communication styles are."""
        sender_style = self.sender.communication_style
        recipient_style = self.recipient.processing_style
        
        compatibility_matrix = {
            ("direct", "decisive"): "high",
            ("direct", "analytical"): "moderate",
            ("analytical", "analytical"): "high",
            ("diplomatic", "collaborative"): "high"
        }
        
        return compatibility_matrix.get((sender_style, recipient_style), "moderate")


def demonstrate_intent_based_communication():
    """Demonstrate the intent-based communication system with realistic examples."""
    
    # Create sample profiles
    ceo_profile = SenderProfile(
        role="CEO",
        communication_style="direct",
        reliability_score=0.9,
        expertise_domains=["strategy", "leadership", "finance"],
        decision_authority_level=10,
        typical_urgency_calibration=0.8,
        trust_level_with_recipient=0.7,
        historical_intent_accuracy=0.85,
        stress_indicators={"overall": 0.6, "workload": 0.7},
        recent_context=["Board meeting pressure", "Q4 performance concerns"]
    )
    
    cfo_profile = RecipientProfile(
        role="CFO",
        processing_style="analytical",
        autonomy_preference=0.6,
        expertise_domains=["finance", "operations", "risk"],
        current_workload=0.8,
        relationship_with_sender="subordinate",
        historical_response_patterns={"action_directive": 0.9, "decision_request": 0.8},
        trust_level_with_sender=0.7,
        current_priorities=["Budget planning", "Financial reporting", "Cost optimization"],
        decision_making_speed="deliberate",
        decision_authority_level=8
    )
    
    # Create intent-based message
    comm_system = IntentBasedMessage(ceo_profile, cfo_profile)
    
    # Sample message
    message_content = "I need you to prepare a comprehensive analysis of our Q4 revenue projections for the board meeting next week. This is critical for our funding discussions."
    
    scenario_context = {
        "urgency": "high",
        "type": "board_revenue_request",
        "deadline": "next_week"
    }
    
    # Generate enhanced message
    enhanced_message = comm_system.create_message(message_content, scenario_context)
    
    # Save demonstration
    output_path = Path("/Users/kenper/src/aprio-one/tech-europe-hackathon/living-twin-synthetic-data/generated/structured/organizations/org_000/flows")
    output_path.mkdir(exist_ok=True)
    
    demo_file = output_path / "intent_based_communication_demo.json"
    with open(demo_file, 'w') as f:
        json.dump(enhanced_message, f, indent=2)
    
    # Generate readable markdown version
    create_intent_demo_markdown(enhanced_message, output_path / "intent_based_communication_demo.md")
    
    print("✅ Intent-based communication system demonstration created")
    print(f"   - JSON data: {demo_file}")
    print(f"   - Readable format: {output_path / 'intent_based_communication_demo.md'}")

def create_intent_demo_markdown(message_data: Dict, output_file: Path):
    """Create readable markdown demonstration of intent-based communication."""
    
    content = f"""# Intent-Based Communication Demonstration

## Message Overview
- **Message ID**: {message_data['message_id']}
- **Timestamp**: {message_data['timestamp']}
- **Raw Content**: "{message_data['raw_content']}"
- **Enhanced Content**: "{message_data['processed_content']}"

## Intent Analysis
### Primary Intent: {message_data['intent_analysis']['primary_intent'].upper()}
- **Secondary Intents**: {', '.join(message_data['intent_analysis']['secondary_intents'])}
- **Intent Confidence**: {message_data['intent_analysis']['intent_confidence']:.2f}
- **Decision Type**: {message_data['intent_analysis']['decision_type']}

## Certainty & Execution Metadata
### Sender Certainty: {message_data['certainty_metadata']['sender_certainty_level'].upper()}
- **Certainty Indicators**: {', '.join(message_data['certainty_metadata']['certainty_indicators'])}
- **Information Completeness**: {message_data['certainty_metadata']['information_completeness']:.2f}
- **Key Assumptions**: {', '.join(message_data['certainty_metadata']['assumption_dependencies'])}

### Execution Expectation: {message_data['execution_metadata']['execution_expectation'].upper()}
- **Urgency Level**: {message_data['execution_metadata']['urgency_level']}
- **Timeline**: {message_data['execution_metadata']['timeline_expectations']}
- **Success Criteria**: {', '.join(message_data['execution_metadata']['success_criteria'])}
- **Resources Needed**: {json.dumps(message_data['execution_metadata']['resource_requirements'])}

## Sender Attribution (What You Know About the Sender)
### Context
- **Role**: {message_data['sender_attribution']['sender_context']['role']}
- **Communication Style**: {message_data['sender_attribution']['sender_context']['communication_style']}
- **Reliability Score**: {message_data['sender_attribution']['sender_context']['reliability_score']:.2f}
- **Authority Level**: {message_data['sender_attribution']['sender_context']['authority_level']}/10
- **Urgency Calibration**: {message_data['sender_attribution']['sender_context']['urgency_calibration']:.2f}

### Historical Patterns
- **Intent Accuracy**: {message_data['sender_attribution']['historical_patterns']['intent_accuracy']:.2f} (How often their stated intent matches reality)
- **Follow-through Rate**: {message_data['sender_attribution']['historical_patterns']['follow_through_rate']:.2f}
- **Typical Response Time**: {message_data['sender_attribution']['historical_patterns']['typical_response_time']}

### Current State
- **Stress Level**: {message_data['sender_attribution']['current_state']['stress_level']:.2f}
- **Workload Pressure**: {message_data['sender_attribution']['current_state']['workload_pressure']:.2f}
- **Relationship Quality**: {message_data['sender_attribution']['current_state']['relationship_quality']:.2f}

### Interpretation Guidance
- **Style Notes**: {message_data['sender_attribution']['interpretation_guidance']['communication_style_notes']}
- **Reliability Context**: {message_data['sender_attribution']['interpretation_guidance']['reliability_context']}

## Recipient Guidance (Intelligent Recommendations)
### Interpretation Analysis
- **Suggested Interpretation**: {message_data['recipient_guidance']['interpretation_analysis']['suggested_interpretation']}
- **Confidence Level**: {message_data['recipient_guidance']['interpretation_analysis']['confidence_in_interpretation']:.2f}
- **Alternative Interpretations**: {', '.join(message_data['recipient_guidance']['interpretation_analysis']['alternative_interpretations'])}
- **Context Dependencies**: {', '.join(message_data['recipient_guidance']['interpretation_analysis']['context_dependencies'])}

### Response Recommendations
- **Recommended Response Type**: {message_data['recipient_guidance']['response_recommendations']['recommended_response_type']}
- **Response Urgency**: {message_data['recipient_guidance']['response_recommendations']['response_urgency']}
- **Key Points to Address**: {', '.join(message_data['recipient_guidance']['response_recommendations']['key_points_to_address'])}
- **Relationship Considerations**: {message_data['recipient_guidance']['response_recommendations']['relationship_considerations']}

### Execution Guidance
- **Immediate Actions**: {', '.join(message_data['recipient_guidance']['execution_guidance']['immediate_actions'])}
- **Decision Points**: {', '.join(message_data['recipient_guidance']['execution_guidance']['decision_points'])}
- **Success Indicators**: {', '.join(message_data['recipient_guidance']['execution_guidance']['success_indicators'])}
- **Risk Factors**: {', '.join(message_data['recipient_guidance']['execution_guidance']['risk_factors'])}

### Escalation Guidance
- **Escalation Triggers**: {', '.join(message_data['recipient_guidance']['escalation_guidance']['escalation_triggers'])}
- **Escalation Path**: {message_data['recipient_guidance']['escalation_guidance']['escalation_path']}
- **Key Stakeholders**: {', '.join(message_data['recipient_guidance']['escalation_guidance']['stakeholders_to_involve'])}

## Relationship Context
- **Relationship Type**: {message_data['relationship_context']['relationship_type']}
- **Trust Level**: {message_data['relationship_context']['trust_level']:.2f}
- **Power Dynamic**: {message_data['relationship_context']['power_dynamic']}
- **Collaboration History**: {message_data['relationship_context']['collaboration_history']}
- **Communication Compatibility**: {message_data['relationship_context']['communication_compatibility']}

---

## Key Innovation: Meaning Over Messages

This system prioritizes **intent, certainty, and execution expectations** over raw message content. 

**Instead of**: "CEO said X to CFO"
**We capture**: 
- WHY they said it (intent)
- HOW certain they are (certainty)  
- WHAT they expect to happen (execution)
- HOW to interpret it (sender context)
- WHAT to do about it (recipient guidance)

This enables true organizational intelligence where people understand not just WHAT was communicated, but the full context of WHY and HOW to act on it effectively.

*Generated by Living Twin Intent-Based Communication System*
"""
    
    with open(output_file, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    demonstrate_intent_based_communication()
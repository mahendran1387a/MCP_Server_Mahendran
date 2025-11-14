"""
Multi-Agent Orchestration System
Coordinates multiple specialized agents for complex tasks
"""
from typing import List, Dict, Any, Optional
from enum import Enum
import asyncio


class AgentRole(Enum):
    """Specialized agent roles"""
    RESEARCHER = "researcher"  # Web search, document analysis
    CODER = "coder"  # Code generation, execution
    ANALYST = "analyst"  # Data analysis, visualization
    WRITER = "writer"  # Documentation, summaries
    PLANNER = "planner"  # Task planning, orchestration
    CRITIC = "critic"  # Review, quality check


class Agent:
    """Base agent class"""

    def __init__(self, role: AgentRole, llm_client, tools: List[str]):
        self.role = role
        self.llm_client = llm_client
        self.tools = tools  # Available tool names
        self.memory = []

    async def think(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Agent thinks about the task"""
        prompt = self._build_prompt(task, context)

        # Use LLM to determine action
        response = await self.llm_client.process_query(prompt)

        return {
            'agent': self.role.value,
            'thought': response,
            'context': context
        }

    def _build_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build prompt based on agent role"""
        base_prompt = f"""You are a specialized {self.role.value} agent.

Task: {task}

Context:
{context}

Your available tools: {', '.join(self.tools)}

What is your next action?"""

        return base_prompt

    def add_to_memory(self, item: Dict[str, Any]):
        """Add to agent's memory"""
        self.memory.append(item)


class MultiAgentOrchestrator:
    """Orchestrates multiple agents to solve complex tasks"""

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.agents = {}
        self.task_history = []

    def create_agent(self, role: AgentRole, tools: List[str]) -> Agent:
        """Create specialized agent"""
        agent = Agent(role, self.llm_client, tools)
        self.agents[role] = agent
        return agent

    def setup_default_agents(self):
        """Setup default agent team"""

        # Researcher: Web scraping, RAG, document processing
        self.create_agent(
            AgentRole.RESEARCHER,
            ['web_extract_text', 'web_search_in_page', 'rag_query',
             'process_pdf', 'summarize_document']
        )

        # Coder: Code execution, analysis, Git
        self.create_agent(
            AgentRole.CODER,
            ['execute_code', 'analyze_code', 'format_code',
             'git_status', 'git_log', 'file_read', 'file_write']
        )

        # Analyst: Data analysis, visualization
        self.create_agent(
            AgentRole.ANALYST,
            ['data_load_csv', 'data_get_summary', 'data_query',
             'data_create_chart']
        )

        # Writer: Documentation, summaries
        self.create_agent(
            AgentRole.WRITER,
            ['summarize_document', 'file_write']
        )

        # Planner: Task decomposition
        self.create_agent(
            AgentRole.PLANNER,
            []  # Uses reasoning, no tools
        )

        # Critic: Quality review
        self.create_agent(
            AgentRole.CRITIC,
            []  # Uses reasoning, no tools
        )

    async def solve_task(self, task: str, agents_needed: Optional[List[AgentRole]] = None) -> Dict[str, Any]:
        """
        Solve complex task using multiple agents

        Args:
            task: Task description
            agents_needed: Optional list of specific agents to use

        Returns:
            Task solution with agent contributions
        """

        # Plan phase: Break down task
        planner = self.agents.get(AgentRole.PLANNER)
        if planner:
            plan = await planner.think(f"Break down this task into steps: {task}", {})
        else:
            plan = {'steps': [task]}

        results = {
            'task': task,
            'plan': plan,
            'agent_contributions': [],
            'final_result': None
        }

        # Execute with agents
        if agents_needed:
            for agent_role in agents_needed:
                agent = self.agents.get(agent_role)
                if agent:
                    contribution = await agent.think(task, results)
                    results['agent_contributions'].append(contribution)

        # Critic review
        critic = self.agents.get(AgentRole.CRITIC)
        if critic:
            review = await critic.think(
                f"Review the solution for: {task}",
                results
            )
            results['review'] = review

        self.task_history.append(results)
        return results

    async def research_task(self, topic: str) -> Dict[str, Any]:
        """Use researcher agent to research a topic"""
        researcher = self.agents.get(AgentRole.RESEARCHER)

        if not researcher:
            return {'error': 'Researcher agent not available'}

        result = await researcher.think(
            f"Research this topic thoroughly: {topic}",
            {'topic': topic}
        )

        return result

    async def code_task(self, requirements: str) -> Dict[str, Any]:
        """Use coder agent to write code"""
        coder = self.agents.get(AgentRole.CODER)

        if not coder:
            return {'error': 'Coder agent not available'}

        # Coder thinks and plans
        plan = await coder.think(
            f"Plan how to implement: {requirements}",
            {'requirements': requirements}
        )

        # Coder implements
        implementation = await coder.think(
            f"Implement the code: {requirements}",
            {'plan': plan}
        )

        # Critic reviews
        critic = self.agents.get(AgentRole.CRITIC)
        if critic:
            review = await critic.think(
                "Review this code implementation",
                {'implementation': implementation}
            )
            implementation['review'] = review

        return implementation

    async def analyze_data_task(self, data_path: str, question: str) -> Dict[str, Any]:
        """Use analyst agent to analyze data"""
        analyst = self.agents.get(AgentRole.ANALYST)

        if not analyst:
            return {'error': 'Analyst agent not available'}

        result = await analyst.think(
            f"Analyze {data_path} to answer: {question}",
            {'data_path': data_path, 'question': question}
        )

        return result

    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get history of all tasks"""
        return self.task_history


class WorkflowOrchestrator:
    """Orchestrates complex workflows"""

    def __init__(self, multi_agent_system: MultiAgentOrchestrator):
        self.agents = multi_agent_system
        self.workflows = {}

    def define_workflow(self, name: str, steps: List[Dict[str, Any]]):
        """
        Define a workflow

        Args:
            name: Workflow name
            steps: List of steps, each with 'agent', 'action', 'inputs'
        """
        self.workflows[name] = steps

    async def execute_workflow(self, name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a defined workflow"""
        if name not in self.workflows:
            return {'error': f'Workflow {name} not found'}

        workflow = self.workflows[name]
        results = {
            'workflow': name,
            'steps': [],
            'inputs': inputs,
            'outputs': {}
        }

        context = inputs.copy()

        for step in workflow:
            agent_role = step.get('agent')
            action = step.get('action')

            agent = self.agents.agents.get(agent_role)

            if not agent:
                results['steps'].append({
                    'step': step,
                    'error': f'Agent {agent_role} not found'
                })
                continue

            # Execute step
            step_result = await agent.think(action, context)

            results['steps'].append({
                'agent': agent_role.value,
                'action': action,
                'result': step_result
            })

            # Update context with result
            context.update(step_result)

        results['outputs'] = context

        return results


# Example workflow definitions
EXAMPLE_WORKFLOWS = {
    "research_and_summarize": [
        {
            "agent": AgentRole.RESEARCHER,
            "action": "Research the topic from web sources",
            "inputs": ["topic"]
        },
        {
            "agent": AgentRole.WRITER,
            "action": "Summarize the research findings",
            "inputs": ["research_results"]
        },
        {
            "agent": AgentRole.CRITIC,
            "action": "Review the summary for accuracy",
            "inputs": ["summary"]
        }
    ],

    "code_review_workflow": [
        {
            "agent": AgentRole.CODER,
            "action": "Analyze the code structure",
            "inputs": ["code_path"]
        },
        {
            "agent": AgentRole.CRITIC,
            "action": "Review code quality and suggest improvements",
            "inputs": ["code_analysis"]
        },
        {
            "agent": AgentRole.WRITER,
            "action": "Document the findings and recommendations",
            "inputs": ["review_results"]
        }
    ],

    "data_analysis_workflow": [
        {
            "agent": AgentRole.ANALYST,
            "action": "Load and explore the dataset",
            "inputs": ["data_path"]
        },
        {
            "agent": AgentRole.ANALYST,
            "action": "Perform statistical analysis",
            "inputs": ["dataset"]
        },
        {
            "agent": AgentRole.ANALYST,
            "action": "Create visualizations",
            "inputs": ["analysis_results"]
        },
        {
            "agent": AgentRole.WRITER,
            "action": "Write analysis report",
            "inputs": ["visualizations", "statistics"]
        }
    ]
}

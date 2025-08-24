from typing import Annotated

from mcp import ServerSession, SamplingMessage
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent
from pydantic import Field, BaseModel

from human_in_the_loop.views import dialogue

def create_server() -> FastMCP:
    mcp_server = FastMCP(name="hw-mcp-human-in-the-loop")

    @mcp_server.tool(
        title="Ask Human",
        description="Ask human for certain information. Especially when you don't know what you are going to do next"
    )
    def ask_human(
            query: Annotated[str, Field(description="The question to ask the human user")],
    ) -> str:
        return dialogue(query)

    @mcp_server.resource("greeting://{name}")
    def get_greeting(name: str) -> str:
        """Get a personalized greeting"""
        return f"Hello, {name}!"

    # Add a prompt
    @mcp_server.prompt()
    def greet_user(name: str, style: str = "friendly") -> str:
        """Generate a greeting prompt"""
        styles = {
            "friendly": "Please write a warm, friendly greeting",
            "formal": "Please write a formal, professional greeting",
            "casual": "Please write a casual, relaxed greeting",
        }

        return f"{styles.get(style, styles['friendly'])} for someone named {name}."

    @mcp_server.tool()
    async def long_running_task(task_name: str, ctx: Context[ServerSession, None], steps: int = 5) -> str:
        """Execute a task with progress updates."""
        await ctx.info(f"Starting: {task_name}")

        for i in range(steps):
            progress = (i + 1) / steps
            await ctx.report_progress(
                progress=progress,
                total=1.0,
                message=f"Step {i + 1}/{steps}",
            )
            await ctx.info(f"Completed step {i + 1}")

        return f"Task '{task_name}' completed"

    class BookingPreferences(BaseModel):
        """Schema for collecting user preferences."""

        checkAlternative: bool = Field(description="Would you like to check another date?")
        alternativeDate: str = Field(
            default="2024-12-26",
            description="Alternative date (YYYY-MM-DD)",
        )

    @mcp_server.tool()
    async def book_table(date: str, time: str, party_size: int, ctx: Context[ServerSession, None]) -> str:
        """Book a table with date availability check."""
        # Check if date is available
        if date == "2024-12-25":
            # Date unavailable - ask user for alternative
            result = await ctx.elicit(
                message=(f"No tables available for {party_size} on {date}. Would you like to try another date?"),
                schema=BookingPreferences,
            )

            if result.action == "accept" and result.data:
                if result.data.checkAlternative:
                    return f"[SUCCESS] Booked for {result.data.alternativeDate}"
                return "[CANCELLED] No booking made"
            return "[CANCELLED] Booking cancelled"

        # Date available
        return f"[SUCCESS] Booked for {date} at {time}"

    @mcp_server.tool()
    async def generate_poem(topic: str, ctx: Context[ServerSession, None]) -> str:
        """Generate a poem using LLM sampling."""
        prompt = f"Write a short poem about {topic}"

        result = await ctx.session.create_message(
            messages=[
                SamplingMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt),
                )
            ],
            max_tokens=100,
        )

        if result.content.type == "text":
            return result.content.text
        return str(result.content)

    return mcp_server

def main():
    print("Starting MCP server...")
    mcp = create_server()
    mcp.run()

from typing import Annotated, Dict

from mcp import ServerSession, SamplingMessage
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent
from pydantic import Field, BaseModel
from mcp_demo.views import dialogue


def create_server() -> FastMCP:
    mcp_server = FastMCP(name="hw-mcp-demo", log_level="ERROR")

    @mcp_server.tool(
        title="Ask Human",
        description="Ask human for certain information. Especially when you don't know what you are going to do next"
    )
    def ask_human(
            query: Annotated[str, Field(description="The question to ask the human user")],
    ) -> str:
        return dialogue(query)

    @mcp_server.tool(
        title="Ask Expert",
        description="Ask expert for specific knowledge. Especially when you don't know how to achieve the target"
    )
    async def ask_expert(
            query: Annotated[str, Field(description="The question to ask the expert")],
            ctx: Context[ServerSession, None]
    ) -> str:
        result = await ctx.session.create_message(
            messages=[
                SamplingMessage(
                    role="user",
                    content=TextContent(type="text", text=query),
                )
            ],
            max_tokens=1024,
        )
        if result.content.type == "text":
            return result.content.text
        return str(result.content)

    @mcp_server.tool(
        title="Run Task",
        description="Run a task"
    )
    async def run_task(
            task_name: Annotated[str, Field(description="The name of the task to run")],
            ctx: Context[ServerSession, None]
    ) -> str:
        await ctx.info(f"Starting: {task_name}")
        for i in range(3):
            await ctx.info(f"Completed step {i + 1}")
        return f"Task '{task_name}' completed"

    @mcp_server.resource(
        uri="user://{user_id}",
        title="Get User Info",
        description="Get User information by user id"
    )
    def get_user_info(
            user_id: Annotated[str, Field(description="The ID of the user")],
    ) -> Dict:
        return {
            "id": user_id,
            "name": "Alice",
            "email": "alice@example.com",
        }

    @mcp_server.prompt(
        title="Ask Question Prompt",
        description="Optimize the answer in area of user experience."
    )
    async def ask_question(
            query: Annotated[str, Field(description="The question to user provided")],
    ) -> str:
        return f"""
        # 人设
        - 你始终使用中文
        - 你是一个人工智能专业的教授
        - 你会用可视化的markdown形式进行输出，例如表格，plantuml，或者latex(需要用$$包裹)。
        
        # 受众
        - 在人工智能方面的基础比较弱，尽量深入浅出的讲解给他（从应用到原理）
        - 近乎零基础，尽量从应用角度一步步推进到理论
        
        # 任务
        {query}
        """

    class BookingPreferences(BaseModel):
        """Schema for collecting user preferences."""

        checkAlternative: bool = Field(description="Would you like to check another date?")
        alternativeDate: str = Field(
            default="2024-12-26",
            description="Alternative date (YYYY-MM-DD)",
        )

    @mcp_server.tool()
    async def book_table(date: str, ctx: Context[ServerSession, None]) -> str:
        """Book a table with date availability check."""
        # Check if date is available
        if date == "2024-12-25":
            # Date unavailable - ask user for alternative
            result = await ctx.elicit(
                message=(f"No tables available on {date}. Would you like to try another date?"),
                schema=BookingPreferences,
            )

            if result.action == "accept" and result.data:
                if result.data.checkAlternative:
                    return f"[SUCCESS] Booked for {result.data.alternativeDate}"
                return "[CANCELLED] No booking made"
            return "[CANCELLED] Booking cancelled"

        # Date available
        return f"[SUCCESS] Booked for {date}"

    return mcp_server


def main():
    print("Starting MCP server...")
    mcp = create_server()
    mcp.run()

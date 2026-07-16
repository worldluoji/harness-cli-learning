from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, tool, create_sdk_mcp_server
import anyio
import os
from dotenv import load_dotenv
import akshare as ak

load_dotenv()

os.environ.setdefault("ANTHROPIC_BASE_URL", "https://dashscope.aliyuncs.com/apps/anthropic")
os.environ.setdefault("ANTHROPIC_MODEL", "qwen3.7-max")
os.environ.setdefault("ANTHROPIC_DEFAULT_HAIKU_MODEL", "qwen3.7-max")
os.environ.setdefault("ANTHROPIC_DEFAULT_SONNET_MODEL", "qwen3.7-max")
os.environ.setdefault("ANTHROPIC_DEFAULT_OPUS_MODEL", "qwen3.7-max")
os.environ.setdefault("ANTHROPIC_AUTH_TOKEN", os.getenv("ALI_API_KEY"))

async def main():
    @tool("getbalance", "获取沪深A股公司的资产负债表，并保存到文件中，其中参数stock_code是带市场标识的股票代码，比如SH600600，参数year是年份", {"stock_code": str, "year": str})
    async def get_balance_sheet_A(stock_code: str = "SH600600", year: str = "2025"):
        try:  
            df_balance_sheet = ak.stock_balance_sheet_by_yearly_em(symbol="SH600600")

            # 只取REPORT_DATE是2025-12-31的数据
            df_balance_sheet = df_balance_sheet[df_balance_sheet['REPORT_DATE'] == f'{year}-12-31 00:00:00']

            # 获取项目根目录（假设当前文件在 0.1/tools/ 目录下）
            project_root = os.getcwd()
            # 去掉SH,SZ前缀
            #stock_code_clean = stock_code[2:] if stock_code.startswith(('SH', 'SZ')) else stock_code
            # 创建完整的文件路径
            filepath = os.path.join(project_root, "data", "financial_statements", f"{stock_code}_{year}_资产负债表.csv")

            # 创建目录（如果不存在）
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 使用指定目录保存文件
            df_balance_sheet.to_csv(filepath, index=False, encoding='utf-8-sig')

            return {
                "content": [
                    {"type": "text", "text": f"资产负债表已保存到: {filepath}"}
                ]
            }

        except Exception as e:
                return {
                    "content": [
                        {"type": "text", "text": f"获取资产负债表失败: {e}"}
                    ]
                }

    # Create an SDK MCP server
    server = create_sdk_mcp_server(
        name="my-tools",
        version="1.0.0",
        tools=[get_balance_sheet_A]
    )

    # Use it with Claude. allowed_tools pre-approves the tool so it runs
    # without a permission prompt; it does not control tool availability.
    options = ClaudeAgentOptions(
        mcp_servers={"tools": server},
        allowed_tools=["mcp__tools__getbalance"]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("获取 SH600600 的2025年度资产负债表")

        # Extract and print response
        async for msg in client.receive_response():
            print(msg)

anyio.run(main)
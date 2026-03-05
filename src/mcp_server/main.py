from mcp_server.server import mcp

# Import tool modules so @mcp.tool() decorators register on startup
import mcp_server.tools.web_browser  # noqa: F401
import mcp_server.tools.document_reader  # noqa: F401


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

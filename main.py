"""
MySQL数据库MCP服务器
专为Cursor IDE集成设计，提供安全的MySQL数据库访问和管理功能

Copyright (c) 2025 qyue
Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from database import get_db_instance
from document_generator import get_doc_generator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
app = Server("mysql-mcp")

# 全局实例
db = None
doc_generator = None


@app.list_resources()
async def list_resources() -> List[Resource]:
    """列出可用的资源"""
    return [
        Resource(
            uri="mysql://database/overview",
            name="数据库概览",
            description="MySQL数据库的完整概览，包括所有表的信息",
            mimeType="text/markdown"
        ),
        Resource(
            uri="mysql://database/tables",
            name="数据库表列表", 
            description="当前数据库中所有表的列表",
            mimeType="application/json"
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """读取指定资源的内容"""
    global db, doc_generator
    
    if db is None:
        db = get_db_instance()
    if doc_generator is None:
        doc_generator = get_doc_generator()
    
    try:
        if uri == "mysql://database/overview":
            return doc_generator.generate_database_overview()
        elif uri == "mysql://database/tables":
            tables = db.get_all_tables()
            return json.dumps(tables, indent=2, default=str, ensure_ascii=False)
        else:
            raise ValueError(f"未知的资源URI: {uri}")
    except Exception as e:
        logger.error(f"读取资源失败 {uri}: {e}")
        raise


@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="test_connection",
            description="测试MySQL数据库连接",
            inputSchema={
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            }
        ),
        Tool(
            name="get_security_info",
            description="获取当前安全配置信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string", 
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            }
        ),
        Tool(
            name="list_tables",
            description="获取数据库中所有表的列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "数据库名称",
                        "default": "public"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="describe_table",
            description="获取指定表的详细结构信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "表名"
                    },
                    "database": {
                        "type": "string",
                        "description": "数据库名称",
                        "default": "public"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="generate_table_doc",
            description="生成表结构设计文档并保存为文件（支持Markdown、JSON、SQL格式）",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "表名"
                    },
                    "database": {
                        "type": "string",
                        "description": "数据库名称",
                        "default": "public"
                    },
                    "format": {
                        "type": "string",
                        "description": "文档格式: markdown, json, sql",
                        "enum": ["markdown", "json", "sql"],
                        "default": "markdown"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="generate_database_overview",
            description="生成数据库概览文档并保存为Markdown文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "数据库名称",
                        "default": "public"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="execute_query",
            description="执行SQL语句（根据安全模式限制操作类型）",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL语句"
                    }
                },
                "required": ["sql"]
            }
        ),
        Tool(
            name="list_schemas",
            description="获取用户有权限访问的所有数据库",
            inputSchema={
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """调用指定的工具"""
    global db, doc_generator
    
    if db is None:
        db = get_db_instance()
    if doc_generator is None:
        doc_generator = get_doc_generator()
    
    try:
        if name == "test_connection":
            result = db.test_connection()
            return [TextContent(
                type="text",
                text=f"数据库连接测试: {'成功' if result else '失败'}"
            )]
        
        elif name == "get_security_info":
            security_info = db.get_security_info()
            return [TextContent(
                type="text",
                text=f"MySQL数据库安全配置:\n{json.dumps(security_info, indent=2, ensure_ascii=False)}"
            )]
        
        elif name == "list_tables":
            database = arguments.get("database")
            tables = db.get_all_tables(database)
            return [TextContent(
                type="text",
                text=f"数据库表列表 ({len(tables)} 个表):\n{json.dumps(tables, indent=2, default=str, ensure_ascii=False)}"
            )]
        
        elif name == "describe_table":
            table_name = arguments["table_name"]
            database = arguments.get("database")
            
            # 获取表结构
            columns = db.get_table_structure(table_name, database)
            indexes = db.get_table_indexes(table_name, database)
            constraints = db.get_table_constraints(table_name, database)
            
            result = {
                "table_name": table_name,
                "database": database or db.config.database,
                "columns": columns,
                "indexes": indexes,
                "constraints": constraints
            }
            
            return [TextContent(
                type="text",
                text=f"表 '{table_name}' 的结构信息:\n{json.dumps(result, indent=2, default=str, ensure_ascii=False)}"
            )]
        
        elif name == "generate_table_doc":
            table_name = arguments["table_name"]
            database = arguments.get("database")
            format_type = arguments.get("format", "markdown")
            
            # 生成文档
            content = doc_generator.generate_table_doc(table_name, database, format_type)
            
            # 保存文档
            timestamp = doc_generator.generation_time.strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{table_name}_structure.{format_type.lower()}"
            filepath = doc_generator.save_document(content, filename)
            
            return [TextContent(
                type="text",
                text=f"表 '{table_name}' 的{format_type.upper()}文档已生成并保存到: {filepath}\n\n文档内容:\n{content[:500]}..."
            )]
        
        elif name == "generate_database_overview":
            database = arguments.get("database")
            
            # 生成概览文档
            content = doc_generator.generate_database_overview(database)
            
            # 保存文档
            timestamp = doc_generator.generation_time.strftime("%Y%m%d_%H%M%S")
            db_name = database or db.config.database
            filename = f"{timestamp}_{db_name}_overview.md"
            filepath = doc_generator.save_document(content, filename)
            
            return [TextContent(
                type="text",
                text=f"数据库 '{db_name}' 的概览文档已生成并保存到: {filepath}\n\n文档内容:\n{content[:500]}..."
            )]
        
        elif name == "execute_query":
            sql = arguments["sql"]
            
            # 执行查询
            results = db.execute_query(sql)
            
            # 格式化结果
            if results:
                result_text = f"查询执行成功，返回 {len(results)} 条记录:\n"
                result_text += json.dumps(results, indent=2, default=str, ensure_ascii=False)
            else:
                result_text = "查询执行成功，无返回结果"
            
            return [TextContent(
                type="text", 
                text=result_text
            )]
        
        elif name == "list_schemas":
            schemas = db.get_available_schemas()
            return [TextContent(
                type="text",
                text=f"可用数据库列表 ({len(schemas)} 个):\n{json.dumps(schemas, indent=2, default=str, ensure_ascii=False)}"
            )]
        
        else:
            raise ValueError(f"未知的工具: {name}")
    
    except Exception as e:
        error_msg = f"工具 '{name}' 执行失败: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def main():
    """主函数 - 启动MCP服务器"""
    # 初始化数据库连接
    global db, doc_generator
    try:
        db = get_db_instance()
        doc_generator = get_doc_generator()
        logger.info("MySQL MCP服务器初始化成功")
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        raise
    
    # 启动stdio服务器
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mysql-mcp",
                server_version="1.0.0",
                            capabilities=app.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
            )
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        raise 
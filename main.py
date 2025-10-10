#!/usr/bin/env python3
"""
MySQL数据库MCP服务
专为Cursor设计，提供表结构查询和文档生成功能
支持多种安全模式

Copyright (c) 2025 qyue
Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Any, Sequence
import logging

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
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
from document_generator import doc_generator
from config import get_config_instance

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_data(data_list):
    """标准化数据，将大小写字段名转换为小写（保持原字段名作为备份）"""
    normalized = []
    for item in data_list:
        normalized_item = {}
        for key, value in item.items():
            # 保留原字段名
            normalized_item[key] = value
            # 添加小写字段名
            normalized_item[key.lower()] = value
        normalized.append(normalized_item)
    return normalized

def create_error_response(error_msg: str, error_type: str = "error") -> list[TextContent]:
    """创建统一的错误响应"""
    logger.error(f"{error_type}: {error_msg}")
    return [TextContent(
        type="text",
        text=f"❌ {error_type.upper()}: {error_msg}"
    )]

def create_success_response(success_msg: str) -> list[TextContent]:
    """创建统一的成功响应"""
    logger.info(f"Success: {success_msg}")
    return [TextContent(
        type="text",
        text=f"✅ {success_msg}"
    )]

# 创建MCP服务器
server = Server("mysql-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    列出可用的工具
    """
    return [
        Tool(
            name="test_connection",
            description="测试MySQL数据库连接",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_security_info",
            description="获取当前安全配置信息",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
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
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_cache_info",
            description="获取查询缓存统计信息",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="clear_cache",
            description="清空查询缓存",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    处理工具调用
    """
    try:
        # 获取数据库实例
        db = get_db_instance()
        if name == "test_connection":
            result = db.test_connection()
            return [TextContent(
                type="text",
                text=f"数据库连接测试: {'成功' if result else '失败'}"
            )]
        
        elif name == "get_security_info":
            security_info = db.get_security_info()
            info_text = "当前安全配置信息:\n\n"
            info_text += f"安全模式: {security_info['security_mode']}\n"
            info_text += f"只读模式: {'是' if security_info['readonly_mode'] else '否'}\n"
            info_text += f"允许写入操作: {'是' if security_info['write_allowed'] else '否'}\n"
            info_text += f"允许危险操作: {'是' if security_info['dangerous_operations_allowed'] else '否'}\n"
            info_text += f"允许访问的数据库: {', '.join(security_info['allowed_schemas'])}\n"
            info_text += f"最大返回行数: {security_info['max_result_rows']}\n"
            info_text += f"查询日志: {'启用' if security_info['query_log_enabled'] else '禁用'}\n"
            
            return [TextContent(type="text", text=info_text)]
        
        elif name == "list_tables":
            database = arguments.get("database") if arguments else None
            tables = db.get_all_tables(database)
            
            if not tables:
                return [TextContent(
                    type="text",
                    text=f"在数据库 '{database or db.config.database}' 中没有找到任何表"
                )]
            
            # 格式化表列表
            table_list = "\n".join([f"- {table.get('tablename', 'Unknown')}" for table in tables])
            return [TextContent(
                type="text",
                text=f"数据库 '{database or db.config.database}' 中的表列表:\n{table_list}\n\n总计: {len(tables)} 个表"
            )]
        
        elif name == "describe_table":
            if not arguments or "table_name" not in arguments:
                return create_error_response("缺少必需的参数 'table_name'", "参数错误")
            
            table_name = arguments["table_name"]
            database = arguments.get("database")
            
            # 获取表结构信息
            structure = db.get_table_structure(table_name, database)
            indexes = db.get_table_indexes(table_name, database)
            constraints = db.get_table_constraints(table_name, database)
            table_comment = db.get_table_comment(table_name, database)
            
            if not structure:
                return [TextContent(
                    type="text",
                    text=f"表 '{table_name}' 在数据库 '{database or db.config.database}' 中不存在"
                )]
            
            # 格式化输出
            result = f"表 '{table_name}' 结构信息:\n\n"
            if table_comment:
                result += f"表注释: {table_comment}\n\n"
            result += "字段列表:\n"
            for col in structure:
                column_name = col.get('column_name', 'Unknown')
                data_type = col.get('data_type', 'Unknown')
                is_nullable = col.get('is_nullable', 'YES')
                is_primary_key = col.get('is_primary_key', 'NO')
                column_comment = col.get('column_comment', '')
                
                result += f"- {column_name} ({data_type}) "
                if is_nullable == 'NO':
                    result += "NOT NULL "
                if is_primary_key == 'YES':
                    result += "[主键] "
                if column_comment:
                    result += f"-- {column_comment}"
                result += "\n"
            
            if indexes:
                result += f"\n索引 ({len(indexes)} 个):\n"
                for idx in indexes:
                    indexname = idx.get('indexname', 'Unknown')
                    is_unique = idx.get('is_unique', 'NO')
                    result += f"- {indexname} {'[唯一]' if is_unique == 'YES' else ''}\n"
            
            if constraints:
                result += f"\n约束 ({len(constraints)} 个):\n"
                for constraint in constraints:
                    constraint_name = constraint.get('constraint_name', 'Unknown')
                    constraint_type = constraint.get('constraint_type', 'Unknown')
                    result += f"- {constraint_name} ({constraint_type})\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "generate_table_doc":
            if not arguments or "table_name" not in arguments:
                return create_error_response("缺少必需的参数 'table_name'", "参数错误")
            
            try:
                table_name = arguments["table_name"]
                database = arguments.get("database")
                format_type = arguments.get("format", "markdown")
                
                # 获取表信息
                structure = db.get_table_structure(table_name, database)
                indexes = db.get_table_indexes(table_name, database)
                constraints = db.get_table_constraints(table_name, database)
                table_comment = db.get_table_comment(table_name, database)
                
                if not structure:
                    return [TextContent(
                        type="text",
                        text=f"表 '{table_name}' 在数据库 '{database or db.config.database}' 中不存在"
                    )]
                
                # 预处理数据
                structure = normalize_data(structure)
                indexes = normalize_data(indexes)
                constraints = normalize_data(constraints)
                
                # 生成文档
                if format_type == "markdown":
                    doc = doc_generator.generate_table_structure_doc(table_name, structure, indexes, constraints, database or db.config.database, table_comment)
                    file_ext = ".md"
                elif format_type == "json":
                    doc = doc_generator.generate_json_structure(table_name, structure, indexes, constraints, database or db.config.database, table_comment)
                    file_ext = ".json"
                elif format_type == "sql":
                    doc = doc_generator.generate_sql_create_statement(table_name, structure, table_comment)
                    file_ext = ".sql"
                else:
                    return [TextContent(
                        type="text",
                        text=f"不支持的文档格式: {format_type}"
                    )]
                
                # 保存文档
                service_dir = os.path.dirname(os.path.abspath(__file__))
                docs_dir = os.path.join(service_dir, "docs")
                os.makedirs(docs_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{database or db.config.database}_{table_name}_{timestamp}{file_ext}"
                file_path = os.path.join(docs_dir, filename)
                
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(doc)
                    
                    relative_path = os.path.relpath(file_path, service_dir)
                    result_text = f"✅ 文档生成成功!\n\n"
                    result_text += f"📁 保存路径: {relative_path}\n"
                    result_text += f"📂 MCP服务目录: {service_dir}\n"
                    result_text += f"📊 表名: {database or db.config.database}.{table_name}\n"
                    result_text += f"📝 格式: {format_type}\n"
                    result_text += f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    result_text += "📄 文档内容预览:\n"
                    result_text += "=" * 50 + "\n"
                    
                    preview = doc[:1000] + "..." if len(doc) > 1000 else doc
                    result_text += preview
                    
                    return [TextContent(type="text", text=result_text)]
                    
                except Exception as file_error:
                    error_msg = f"⚠️ 文件保存失败: {str(file_error)}\n\n"
                    error_msg += "📄 生成的文档内容:\n"
                    error_msg += "=" * 50 + "\n"
                    error_msg += doc
                    return [TextContent(type="text", text=error_msg)]
            
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"生成文档时发生错误: {str(e)}"
                )]
        
        elif name == "generate_database_overview":
            try:
                database = arguments.get("database") if arguments else None
                tables = db.get_all_tables(database)
                
                # 预处理数据
                tables = normalize_data(tables)
                
                # 生成文档
                doc = doc_generator.generate_database_overview_doc(tables, database or db.config.database)
                
                # 保存文档
                service_dir = os.path.dirname(os.path.abspath(__file__))
                docs_dir = os.path.join(service_dir, "docs")
                os.makedirs(docs_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{database or db.config.database}_数据库概览_{timestamp}.md"
                file_path = os.path.join(docs_dir, filename)
                
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(doc)
                    
                    relative_path = os.path.relpath(file_path, service_dir)
                    result_text = f"✅ 数据库概览文档生成成功!\n\n"
                    result_text += f"📁 保存路径: {relative_path}\n"
                    result_text += f"📂 MCP服务目录: {service_dir}\n"
                    result_text += f"🗂️ 数据库: {database or db.config.database}\n"
                    result_text += f"📋 表数量: {len(tables)} 个\n"
                    result_text += f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    result_text += "📄 文档内容预览:\n"
                    result_text += "=" * 50 + "\n"
                    
                    preview = doc[:1000] + "..." if len(doc) > 1000 else doc
                    result_text += preview
                    
                    return [TextContent(type="text", text=result_text)]
                    
                except Exception as file_error:
                    error_msg = f"⚠️ 文件保存失败: {str(file_error)}\n\n"
                    error_msg += "📄 生成的文档内容:\n"
                    error_msg += "=" * 50 + "\n"
                    error_msg += doc
                    return [TextContent(type="text", text=error_msg)]
                    
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"生成数据库概览文档时发生错误: {str(e)}"
                )]
        
        elif name == "execute_query":
            if not arguments or "sql" not in arguments:
                return create_error_response("缺少必需的参数 'sql'", "参数错误")
            
            sql = arguments["sql"]
            
            try:
                results = db.execute_query(sql)
                
                if not results:
                    return [TextContent(
                        type="text",
                        text="语句执行成功，但没有返回结果"
                    )]
                
                # 格式化结果
                if sql.upper().strip().startswith(('SELECT', 'WITH', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                    result_text = f"查询结果 ({len(results)} 条记录):\n\n"
                    
                    if len(results) <= 100:  # 限制显示条数
                        result_text += json.dumps(results, ensure_ascii=False, indent=2, default=str)
                    else:
                        result_text += f"结果集过大，仅显示前100条:\n"
                        result_text += json.dumps(results[:100], ensure_ascii=False, indent=2, default=str)
                        result_text += f"\n\n... (还有 {len(results) - 100} 条记录)"
                else:
                    # 非查询操作的结果
                    result_text = f"操作执行成功:\n\n"
                    result_text += json.dumps(results, ensure_ascii=False, indent=2, default=str)
                
                return [TextContent(type="text", text=result_text)]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"SQL执行失败: {str(e)}"
                )]
        
        elif name == "list_schemas":
            try:
                schemas = db.get_available_schemas()
                
                if not schemas:
                    return [TextContent(
                        type="text",
                        text="没有找到可访问的数据库"
                    )]
                
                schema_list = "\n".join([f"- {schema.get('schemaname', 'Unknown')}" for schema in schemas])
                
                config_info = f"当前数据库访问策略: {db._get_allowed_schemas_display()}\n\n"
                result_text = config_info + f"可访问的数据库:\n{schema_list}\n\n总计: {len(schemas)} 个数据库"
                
                return [TextContent(type="text", text=result_text)]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"获取数据库列表失败: {str(e)}"
                )]
        
        elif name == "get_cache_info":
            try:
                cache_info = db.get_cache_info()
                
                result_text = "📊 查询缓存统计信息:\n\n"
                result_text += f"缓存大小: {cache_info['cache_size']} / {cache_info['max_size']} 条\n"
                result_text += f"缓存TTL: {cache_info['ttl']} 秒\n"
                result_text += f"缓存条目数: {len(cache_info['entries'])} 个\n\n"
                
                if cache_info['entries']:
                    result_text += "📋 缓存条目:\n"
                    for i, entry in enumerate(cache_info['entries'][:10], 1):  # 只显示前10个
                        result_text += f"{i}. {entry[:20]}...\n"
                    if len(cache_info['entries']) > 10:
                        result_text += f"... 还有 {len(cache_info['entries']) - 10} 个条目\n"
                
                return [TextContent(type="text", text=result_text)]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"获取缓存信息失败: {str(e)}"
                )]
        
        elif name == "clear_cache":
            try:
                db.clear_cache()
                return [TextContent(
                    type="text",
                    text="✅ 查询缓存已清空"
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"清空缓存失败: {str(e)}"
                )]
        
        else:
            return create_error_response(f"未知的工具: {name}", "工具错误")
    
    except Exception as e:
        return create_error_response(f"工具调用失败: {str(e)}", "系统错误")

async def main():
    """主函数"""
    # 初始化配置和数据库连接测试
    logger.info("启动MySQL数据库MCP服务...")
    
    try:
        # 获取配置信息
        config = get_config_instance()
        logger.info(f"配置加载成功，安全模式: {config.security_mode.value}")
        
        # 获取数据库实例并测试连接
        db = get_db_instance()
        if db.test_connection():
            logger.info("MySQL数据库连接测试成功")
        else:
            logger.warning("MySQL数据库连接测试失败，服务仍将启动")
            
    except Exception as e:
        logger.error(f"服务初始化失败: {e}")
        logger.error("请检查Cursor MCP配置中的环境变量设置")
        sys.exit(1)
    
    # 启动stdio服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mysql-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main()) 
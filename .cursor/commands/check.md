在执行任何代码任务之前，你必须**并行**调用以下三个工具获取最新信息：

1. **Context7** (`mcp_context7_resolve-library-id` → `mcp_context7_get-library-docs`)
   - 查询相关技术/库的最新文档

2. **DeepWiki** (`mcp_deepwiki_ask_question`)
   - 去 GitHub 找类似项目或官方仓库的实现参考

3. **WebSearch** (`web_search`)
   - 搜索 "[关键技术] 2025" 获取最新信息和最佳实践

## 执行规则
- 三个工具**同时调用**，不要一个一个来
- 不需要问我，直接查
- 查完再写代码
- 当前时间：2025年12月

## 输出格式
查询完成后，简要总结发现的关键信息，然后开始执行任务。


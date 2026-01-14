// 个性化文本工具函数
// 将 {{name}} 占位符替换为用户姓名

/**
 * 替换文本中的 {{name}} 占位符
 * @param text 原始文本
 * @param name 用户姓名
 * @returns 替换后的文本
 */
export function personalizeText(text: string | undefined, name: string | null): string {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'personalize.ts:10',message:'personalizeText',data:{textType:typeof text,textPreview:String(text)?.substring(0,30),nameType:typeof name,name:name},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'C'})}).catch(()=>{});
  // #endregion
  if (!text) return ''
  
  // 如果没有名字，使用 "there" 作为默认值
  const displayName = name?.trim() || 'there'
  
  return text.replace(/\{\{name\}\}/g, displayName)
}


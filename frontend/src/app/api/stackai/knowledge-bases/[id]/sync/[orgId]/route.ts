import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.STACKAI_BACKEND_URL!

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; orgId: string }> }
) {
  try {
    const authHeader = request.headers.get('authorization')
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      )
    }

    const { id: knowledgeBaseId, orgId } = await params
    
    console.log('🔄 Server: Syncing knowledge base:', knowledgeBaseId)

    // Trigger sync using Stack AI API
    const response = await fetch(`${BACKEND_URL}/knowledge_bases/sync/trigger/${knowledgeBaseId}/${orgId}`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ Server: KB sync failed:', errorText)
      return NextResponse.json(
        { error: `Failed to sync knowledge base: ${response.statusText}` },
        { status: response.status }
      )
    }

    console.log('✅ Server: Knowledge base sync triggered')

    return NextResponse.json({ success: true })

  } catch (error) {
    console.error('❌ Server: Knowledge base sync error:', error)
    return NextResponse.json(
      { error: 'Internal server error during knowledge base sync' },
      { status: 500 }
    )
  }
} 
import { NextRequest, NextResponse } from 'next/server'
import { api } from '@/lib/logger'

const BACKEND_URL = process.env.STACKAI_BACKEND_URL!

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; orgId: string }> }
) {
  try {
    const { id: knowledgeBaseId, orgId } = await params
    const accessToken = request.headers.get('x-access-token')

    if (!BACKEND_URL) {
      api.error('Missing STACKAI_BACKEND_URL environment variable')
      return NextResponse.json(
        { error: 'Server configuration error: Missing backend URL' },
        { status: 500 }
      )
    }

    if (!accessToken) {
      return NextResponse.json({ error: 'Access token required' }, { status: 401 })
    }

    // Forward the request to Stack AI API - using GET as per notebook
    const url = `${BACKEND_URL}/knowledge_bases/sync/trigger/${knowledgeBaseId}/${orgId}`
    api.debug('Triggering KB sync via API', { url, knowledgeBaseId, orgId })

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      api.error('Knowledge base sync failed', { error: errorText, status: response.status })
      return NextResponse.json(
        { error: `Failed to sync knowledge base: ${response.statusText}` },
        { status: response.status }
      )
    }

    const data = await response.text()
    api.info('Knowledge base sync triggered', { knowledgeBaseId })

    return NextResponse.json({ success: true, message: data })

  } catch (error) {
    api.error('Knowledge base sync error', { error })
    return NextResponse.json(
      { error: 'Internal server error while syncing knowledge base' },
      { status: 500 }
    )
  }
} 
import { NextRequest, NextResponse } from 'next/server'
import { api } from '@/lib/logger'

const BACKEND_URL = process.env.STACKAI_BACKEND_URL!

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: knowledgeBaseId } = await params
    const accessToken = request.headers.get('x-access-token')
    const { searchParams } = new URL(request.url)
    const resourcePath = searchParams.get('resource_path')

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

    if (!resourcePath) {
      return NextResponse.json({ error: 'Resource path required' }, { status: 400 })
    }

    // Forward the request to Stack AI API
    const url = `${BACKEND_URL}/knowledge_bases/${knowledgeBaseId}/resources?resource_path=${encodeURIComponent(resourcePath)}`
    api.debug('De-indexing file via API', { url, resourcePath })

    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ resource_path: resourcePath }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      api.error('De-indexing failed', { error: errorText, status: response.status })
      return NextResponse.json(
        { error: `Failed to de-index file: ${response.statusText}` },
        { status: response.status }
      )
    }

    api.info('File de-indexed', { resourcePath })

    return NextResponse.json({ success: true, message: 'File de-indexed successfully' })

  } catch (error) {
    api.error('De-indexing error', { error })
    return NextResponse.json(
      { error: 'Internal server error while de-indexing file' },
      { status: 500 }
    )
  }
} 
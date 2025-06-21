import { NextRequest, NextResponse } from 'next/server'
import { api } from '@/lib/logger'

const BACKEND_URL = process.env.STACKAI_BACKEND_URL!

export async function POST(request: NextRequest) {
  try {
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

    const body = await request.json()
    
    // Forward the request to Stack AI API
    const url = `${BACKEND_URL}/knowledge_bases`
    api.debug('Creating knowledge base via API', { url })

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorText = await response.text()
      api.error('Knowledge base creation failed', { error: errorText, status: response.status })
      return NextResponse.json(
        { error: `Failed to create knowledge base: ${response.statusText}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    api.info('Knowledge base created', { id: data.knowledge_base_id })

    return NextResponse.json(data)

  } catch (error) {
    api.error('Knowledge base creation error', { error })
    return NextResponse.json(
      { error: 'Internal server error while creating knowledge base' },
      { status: 500 }
    )
  }
} 
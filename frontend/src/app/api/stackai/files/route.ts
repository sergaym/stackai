import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.STACKAI_BACKEND_URL!

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const connectionId = searchParams.get('connectionId')
    const parentResourceId = searchParams.get('parentResourceId')
    const accessToken = request.headers.get('x-access-token')

    // Validate required environment variables
    if (!BACKEND_URL) {
      console.error('❌ Server: Missing STACKAI_BACKEND_URL environment variable')
      return NextResponse.json(
        { error: 'Server configuration error: Missing backend URL' },
        { status: 500 }
      )
    }

    if (!accessToken) {
      return NextResponse.json({ error: 'Access token required' }, { status: 401 })
    }

    if (!connectionId) {
      return NextResponse.json({ error: 'Connection ID required' }, { status: 400 })
    }

    // Build the Stack AI API URL
    let url = `${BACKEND_URL}/connections/${connectionId}/resources/children`
    
    if (parentResourceId && parentResourceId !== 'root') {
      url += `?resource_id=${parentResourceId}`
    }

    console.log('📡 Server: Fetching files from:', url)

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ Server: Files fetch failed:', errorText)
      return NextResponse.json(
        { error: `Failed to fetch files: ${response.statusText}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    console.log(`✅ Server: Fetched ${data.data?.length || 0} files`)

    return NextResponse.json(data)

  } catch (error) {
    console.error('❌ Server: Files fetch error:', error)
    return NextResponse.json(
      { error: 'Internal server error while fetching files' },
      { status: 500 }
    )
  }
} 
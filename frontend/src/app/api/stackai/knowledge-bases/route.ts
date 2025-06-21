import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.STACKAI_BACKEND_URL!

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization')
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      )
    }

    const body = await request.json()
    
    console.log('🏗️ Server: Creating knowledge base:', body.name)

    // Create knowledge base using Stack AI API
    const response = await fetch(`${BACKEND_URL}/knowledge_bases`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ Server: KB creation failed:', errorText)
      return NextResponse.json(
        { error: `Failed to create knowledge base: ${response.statusText}` },
        { status: response.status }
      )
    }

    const result = await response.json()
    console.log('✅ Server: Knowledge base created:', result.knowledge_base_id)

    return NextResponse.json(result)

  } catch (error) {
    console.error('❌ Server: Knowledge base creation error:', error)
    return NextResponse.json(
      { error: 'Internal server error during knowledge base creation' },
      { status: 500 }
    )
  }
} 
import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type RouteParams = { params: Promise<{ path: string[] }> }

/**
 * Proxy para todas las peticiones a FastAPI
 * Envía el token desde la cookie httpOnly
 */
export async function GET(request: NextRequest, { params }: RouteParams) {
  const { path } = await params
  return handleRequest(request, path, 'GET')
}

export async function POST(request: NextRequest, { params }: RouteParams) {
  const { path } = await params
  return handleRequest(request, path, 'POST')
}

export async function PUT(request: NextRequest, { params }: RouteParams) {
  const { path } = await params
  return handleRequest(request, path, 'PUT')
}

export async function DELETE(request: NextRequest, { params }: RouteParams) {
  const { path } = await params
  return handleRequest(request, path, 'DELETE')
}

export async function PATCH(request: NextRequest, { params }: RouteParams) {
  const { path } = await params
  return handleRequest(request, path, 'PATCH')
}

async function handleRequest(request: NextRequest, pathArray: string[], method: string) {
  try {
    const cookieStore = await cookies()
    const token = cookieStore.get('access_token')?.value

    if (!token) {
      return NextResponse.json({ detail: 'No autenticado' }, { status: 401 })
    }

    // Construir path
    // El path puede venir como ["api", "v1", "contacts"] o ["contacts"]
    let path = pathArray.join('/')

    // Si ya incluye "api/v1", usarlo directamente
    // Si no, agregarlo
    if (!path.startsWith('api/v1')) {
      path = `api/v1/${path}`
    }

    const url = new URL(request.url)
    const queryString = url.search

    // Headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    }

    // Body para POST/PUT/PATCH
    let body: string | undefined
    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      try {
        const requestBody = await request.json()
        body = JSON.stringify(requestBody)
      } catch {
        // No body
      }
    }

    // Llamar a FastAPI
    const response = await fetch(`${API_URL}/${path}${queryString}`, {
      method,
      headers,
      body,
    })

    const data = await response.json()

    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('Proxy error:', error)
    return NextResponse.json({ detail: 'Error en el proxy' }, { status: 500 })
  }
}

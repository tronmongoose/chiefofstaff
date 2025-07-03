import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = searchParams.get('limit') || '10';
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    
    const response = await fetch(`${backendUrl}/api/reputation/leaderboard?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching leaderboard data:', error);
    return NextResponse.json(
      { 
        status: 'error', 
        message: 'Failed to fetch leaderboard data',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 
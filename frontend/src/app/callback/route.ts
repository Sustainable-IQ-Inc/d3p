import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

// Helper function to get client IP address
function getClientIp(req: NextRequest): string {
    // Check for forwarded IP addresses (Cloud Run, proxies, load balancers)
    const forwarded = req.headers.get('x-forwarded-for');
    if (forwarded) {
        // X-Forwarded-For can contain multiple IPs, the first one is the original client
        return forwarded.split(',')[0].trim();
    }
    
    // Check for real IP header
    const realIp = req.headers.get('x-real-ip');
    if (realIp) {
        return realIp;
    }
    
    return 'unknown';
}

// Helper function to log auth events
async function logAuthEvent(data: {
    event_type: string;
    user_id?: string;
    magic_link_url?: string;
    ip_address?: string;
    error_message?: string;
}) {
    try {
        // Use NEXT_PUBLIC_API_BASE_URL if available, otherwise fall back to localhost
        const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
        await fetch(`${apiUrl}/log-auth-event/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
    } catch (error) {
        // Silently fail - we don't want logging to break the auth flow
        console.error('Failed to log auth event:', error);
    }
}

export async function GET(req: NextRequest){
    const url = new URL(req.url)

    // Get the correct origin from headers (Cloud Run uses X-Forwarded-Host)
    const forwardedHost = req.headers.get('x-forwarded-host');
    const forwardedProto = req.headers.get('x-forwarded-proto') || 'https';
    const correctOrigin = forwardedHost ? `${forwardedProto}://${forwardedHost}` : url.origin;

    const code = url.searchParams.get('code')
    const error = url.searchParams.get('error')
    const errorCode = url.searchParams.get('error_code')
    const errorDescription = url.searchParams.get('error_description')
    
    // Get client IP for logging
    const clientIp = getClientIp(req);

    // Check for errors from Supabase (expired links, etc.)
    if (error) {
        // Create user-friendly error message
        let message = errorDescription || error;
        
        // Customize message for common errors
        if (errorCode === 'otp_expired' || error === 'access_denied') {
            message = 'This magic link has expired or has already been used. Please request a new one by entering your email address below.';
        }
        
        // Log the error
        await logAuthEvent({
            event_type: 'magic_link_error',
            magic_link_url: url.toString(),
            ip_address: clientIp,
            error_message: message,
        });
        
        const encodedMessage = encodeURIComponent(message);
        return NextResponse.redirect(`${correctOrigin}/login?error=auth_failed&message=${encodedMessage}`);
    }

    if(code){
        const cookieStore = await cookies();

        const supabase = createRouteHandlerClient({
            cookies: () => cookieStore
        })
        
        try {
            const { data, error: exchangeError } = await supabase
                .auth
                .exchangeCodeForSession(code)
            
            if (exchangeError) {
                console.error('Error exchanging code for session:', exchangeError);
                
                // Log the error
                await logAuthEvent({
                    event_type: 'magic_link_error',
                    magic_link_url: url.toString(),
                    ip_address: clientIp,
                    error_message: exchangeError.message,
                });
                
                const message = encodeURIComponent(exchangeError.message);
                return NextResponse.redirect(`${correctOrigin}/login?error=auth_failed&message=${message}`);
            }
            
            if (data?.session) {
                // Log successful magic link access
                await logAuthEvent({
                    event_type: 'magic_link_accessed',
                    user_id: data.session.user.id,
                    magic_link_url: url.toString(),
                    ip_address: clientIp,
                });
                
                console.log(`Magic link successfully accessed by user ${data.session.user.id} from IP ${clientIp}`);
                return NextResponse.redirect(`${correctOrigin}/dashboard/default`);
            } else {
                // Log the error
                await logAuthEvent({
                    event_type: 'magic_link_error',
                    magic_link_url: url.toString(),
                    ip_address: clientIp,
                    error_message: 'No session established from magic link',
                });
                
                return NextResponse.redirect(`${correctOrigin}/login?error=auth_failed&message=${encodeURIComponent('No session established from magic link')}`);
            }
        } catch (err) {
            console.error('Unexpected error during code exchange:', err);
            
            // Log the error
            await logAuthEvent({
                event_type: 'magic_link_error',
                magic_link_url: url.toString(),
                ip_address: clientIp,
                error_message: (err as Error)?.message || 'Unexpected authentication error',
            });
            
            const message = encodeURIComponent((err as Error)?.message || 'Unexpected authentication error');
            return NextResponse.redirect(`${correctOrigin}/login?error=auth_failed&message=${message}`);
        }
    }

    // No code provided, redirect to login
    return NextResponse.redirect(`${correctOrigin}/login`)

}
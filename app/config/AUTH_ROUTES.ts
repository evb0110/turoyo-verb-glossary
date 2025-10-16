export const AUTH_ROUTES = {

    public: ['/login', '/blocked'] as const,

    admin: ['/admin'] as const,

    redirectTargets: {
        guest: '/login',
        blocked: '/blocked',
        authenticated: '/',
        unauthorized: '/',
    },
} as const

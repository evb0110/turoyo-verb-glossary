import { getCurrentUser } from '~~/server/repositories/auth/getCurrentUser'

export default defineEventHandler(async (event) => {
    try {
        const userData = await getCurrentUser(event)

        if (!userData) {
            setResponseStatus(event, 401)
            return null
        }

        return userData
    }
    catch (error) {
        console.error('Error fetching user:', error)
        setResponseStatus(event, 500)
        return null
    }
})

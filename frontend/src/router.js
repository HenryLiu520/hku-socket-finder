import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Rooms from './views/Rooms.vue'
import RoomView from './views/RoomView.vue'
import Maintenance from './views/Maintenance.vue'
import Report from './views/Report.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', component: Rooms },
  { path: '/rooms/:id', component: RoomView },
  { path: '/report', component: Report },
  { path: '/maintenance', component: Maintenance, meta: { maintenance: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const token = localStorage.getItem('sf_token')
  const user = JSON.parse(localStorage.getItem('sf_user') || 'null')
  if (!to.meta.public && !token) return '/login'
  if (to.meta.maintenance && (!user || user.role !== 'MAINTENANCE')) return '/'
  if (to.path === '/login' && token) return '/'
  return true
})

export default router

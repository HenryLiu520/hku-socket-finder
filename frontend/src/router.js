import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Rooms from './views/Rooms.vue'
import RoomView from './views/RoomView.vue'
import Maintenance from './views/Maintenance.vue'
import Report from './views/Report.vue'
import MobileShell from './mobile/MobileShell.vue'
import MFind from './mobile/views/MFind.vue'
import MRoom from './mobile/views/MRoom.vue'
import MReport from './mobile/views/MReport.vue'
import MMe from './mobile/views/MMe.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', component: Rooms },
  { path: '/rooms/:id', component: RoomView },
  { path: '/report', component: Report },
  { path: '/maintenance', component: Maintenance, meta: { maintenance: true } },

  /**
   * The handset build. One shell owns the top bar and the four-tab bar; each
   * screen below it is a card page, and `meta.tab` tells the tab bar what to
   * light up. The desktop views above are untouched.
   */
  {
    path: '/m',
    component: MobileShell,
    meta: { mobile: true },
    children: [
      { path: '', name: 'm-find', component: MFind, meta: { tab: 'find' } },
      { path: 'rooms/:id', name: 'm-room', component: MRoom, meta: { tab: 'room' } },
      { path: 'report', name: 'm-report', component: MReport, meta: { tab: 'report' } },
      { path: 'me', name: 'm-me', component: MMe, meta: { tab: 'me' } }
    ]
  },

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

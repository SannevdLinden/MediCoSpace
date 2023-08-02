import Vue from 'vue'
import App from './App.vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import {faAngleRight} from '@fortawesome/free-solid-svg-icons'
import {faCheck} from '@fortawesome/free-solid-svg-icons'
require('@/assets/main.scss');

library.add(faAngleRight, faCheck)

Vue.use(require('vue-moment'))
Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')

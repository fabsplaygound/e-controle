<template>
  <div class="card">
    <div class="card-status card-status-top bg-blue"></div>
    <div class="card-header">
      <div class="card-title">
        <i class="fe fe-users mr-2"></i>
        <span>Qui a accès à cet espace ?</span>
      </div>
    </div>

    <div class="card-body">
      <div class="card">
        <div class="card-header justify-content-between">
          <h3 class="card-title"><i class="fa fa-university mr-2"></i><strong>Équipe de contrôle</strong></h3>
          <a v-if="sessionUser.is_inspector"
             href="javascript:void(0)"
             data-toggle="modal"
             data-target="#addUserModal"
             @click="updateEditingState('inspector')"
             class="btn btn-primary">
            <i class="fe fe-plus"></i>
            Ajouter un contrôleur
          </a>
        </div>
        <user-list :users="inspectorUsers()" profile-type="inspector" :control="control"></user-list>
      </div>

      <div class="card mb-0">
        <div class="card-header justify-content-between">
          <h3 class="card-title"><i class="fa fa-building mr-2"></i><strong>Organisme interrogé</strong></h3>
          <a v-if="sessionUser.is_inspector"
             href=""
             data-toggle="modal"
             data-target="#addUserModal"
             @click="updateEditingState('audited')"
             class="btn btn-primary">
            <i class="fe fe-plus"></i>
            Ajouter une personne
          </a>
        </div>
        <user-list :users="auditedUsers()" profile-type="audited" :control="control"></user-list>
      </div>
    </div>
  </div>

</template>

<script lang="ts">
  import { mapFields } from 'vuex-map-fields'
  import axios from "axios"
  import Vue from "vue";
  import VueAxios from "vue-axios"

  import { store } from '../store'
  import CollapsibleSection from '../utils/CollapsibleSection'
  import EventBus from '../events'
  import UserList from "./UserList"


  Vue.use(VueAxios, axios)


  export default Vue.extend({
    store,
    props: {
      control: Object,
    },
    data() {
      return {
        users: []
      }
    },
    computed: {
      ...mapFields([
        'editingControl',
        'editingProfileType',
        'sessionUser',
      ]),
    },
    methods: {
      getUsers() {
        Vue.axios.get('/api/user/', {
          params: {
            controls: this.control.id
          }
        }).then((response) => {
          this.users = response.data
        })
      },
      auditedUsers() {
        return this.users.filter(item => {
           return item.profile_type === 'audited'
        })
      },
      inspectorUsers() {
        return this.users.filter(item => {
           return item.profile_type === 'inspector'
        })
      },
      updateEditingState(profileType) {
        this.editingControl = this.control
        this.editingProfileType = profileType
      }
    },
    mounted() {
      this.getUsers()
      EventBus.$on('users-changed', () => {
        this.getUsers()
      })
    },
    components: {
      CollapsibleSection,
      UserList,
    }
  });
</script>

<style></style>

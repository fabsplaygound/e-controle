<template>
<div>
  <div class="container">
    <swap-editor-button v-if="controlHasMultipleInspectors"
                        :control-id="controlId"
                        @save-draft="saveDraftAndSwapEditor">
    </swap-editor-button>
    <div class="page-header">
      <div class="page-title flex-wrap">
        <i class="fe fe-list mr-2"></i>
        <span v-if="currentQuestionnaire.is_draft || currentQuestionnaire.id === undefined"
              class="tag tag-azure big-tag round-tag font-italic mr-2">
          Brouillon
        </span>
        <span>
          Rédaction du Questionnaire n°{{ questionnaireNumbering }}
        </span>
        <span v-if="currentQuestionnaire.title" class="ml-1">
          - {{ currentQuestionnaire.title }}
        </span>
      </div>
    </div>
    <div v-if="hasErrors" class="alert alert-danger" id="questionnaire-create-error">
      {{ errorMessage }}
    </div>

    <wizard id="wizard"
            :active-step-number="this.state"
            :step-titles="['Renseigner l\'introduction',
                           'Ajouter des questions',
                           'Aperçu avant publication']"
            @next="next"
            @previous="back">
    </wizard>

    <questionnaire-metadata-create
            id="questionnaire-metadata-create"
            ref="questionnaireMetadataCreate"
            :questionnaire-numbering="questionnaireNumbering"
            v-show="state === STATES.START">
    </questionnaire-metadata-create>
    <questionnaire-body-create
            id="questionnaire-body-create"
            ref="questionnaireBodyCreate"
            v-show="state === STATES.CREATING_BODY">
    </questionnaire-body-create>
    <questionnaire-preview
            id="questionnaire-preview"
            v-show="state === STATES.PREVIEW">
    </questionnaire-preview>

  </div>
  <div id="bottom-bar"
        class="flex-column bg-white sticky-bottom border-top p-4">
    <div id="button-bar" class="flex-row justify-content-between">
      <button id="go-home-button"
              type="button"
              class="btn btn-secondary"
              @click="saveDraftAndGoHome"
      >
        < Retour
      </button>
      <div>
        <button v-if="state !== STATES.START"
                id="back-button"
                @click="back"
                class="btn btn-secondary">
          < Etape {{ state - 1 }}
        </button>
        <button v-if="state === STATES.CREATING_BODY"
                role="button"
                type="button"
                class="btn btn-secondary"
                @click="saveAndShowMoveThemesModal"
                title="Réorganiser les thèmes">
          <i class="fa fa-exchange-alt fa-rotate-90"></i>
          Réorganiser les thèmes
        </button>
        <button @click="validateFormAndSaveDraft"
                class="btn btn-primary">
          <i class="fe fe-save"></i>
          Enregistrer
        </button>
        <button v-if="state !== STATES.PREVIEW"
                id="next-button"
                @click="next"
                class="btn btn-secondary">
          Etape {{ state + 1 }} >
        </button>
        <button v-if="state === STATES.PREVIEW"
                id="publishButton"
                ref="publishButton"
                @click="showPublishConfirmModal()"
                class="btn btn-primary ml-5"
                title="Publier le questionnaire à l'organisme interrogé">
          <i class="fa fa-rocket mr-1"></i>
          Publier
        </button>
      </div>
    </div>
    <div class="flex-row justify-content-end mt-2">
      <div class="text-muted" style="min-height: 1.5rem;">
        {{ saveMessage }}
      </div>
    </div>
  </div>

  <publish-confirm-modal id="publishConfirmModal"
                          ref="publishConfirmModal"
                          :error="publishError"
                          @confirm="publish()"
  >
  </publish-confirm-modal>
  <empty-modal id="savingModal"
                ref="savingModal"
                no-close="true">
    <div class="d-flex flex-column align-items-center p-8">
      <div class="m-4">
        Questionnaire en cours de publication ...
      </div>
      <div class="loader m-4">
      </div>
    </div>
  </empty-modal>
  <empty-modal id="savedModal"
                ref="savedModal"
                no-close="true">
    <div class="modal-header border-bottom-0 flex-column align-items-center">
      <p>
        <i class="fe fe-check-circle fg-success big-icon"></i>
      </p>
      <h4 class="text-center">
        Bravo, votre questionnaire est publié!
      </h4>
    </div>
    <div class="modal-body text-center">
      <p>
        Si des réponses sont déposées par l'organisme interrogé, vous recevrez un email de
        notification dès le lendemain 8 heures.
      </p>
    </div>
    <div class="modal-footer border-top-0 d-flex justify-content-center">
      <button type="button"
              class="btn btn-primary"
              @click="goHome"
      >
        < Revenir à l'accueil
      </button>
    </div>
  </empty-modal>
</div>
</template>

<script>
import axios from 'axios'
import backend from '../utils/backend'
import EmptyModal from '../utils/EmptyModal'
import { loadStatuses } from '../store'
import moment from 'moment'
import { mapFields } from 'vuex-map-fields'
import PublishConfirmModal from './PublishConfirmModal'
import QuestionnaireBodyCreate from './QuestionnaireBodyCreate'
import QuestionnaireMetadataCreate from './QuestionnaireMetadataCreate'
import QuestionnairePreview from './QuestionnairePreview'
import StickyBottomMixin from '../utils/StickyBottomMixin'
import SwapEditorButton from '../editors/SwapEditorButton'
import Vue from 'vue'
import Wizard from '../utils/Wizard'

// State machine
const STATES = {
  START: 1,
  CREATING_BODY: 2,
  PREVIEW: 3,
}

const PUBLISH_TIME_MILLIS = 3000
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default Vue.extend({
  props: {
    controlId: Number,
    controlHasMultipleInspectors: Boolean,
    questionnaireId: Number,
    questionnaireNumbering: Number,
    // Pass window dependency for testing
    window: {
      default: () => window,
    },
  },
  data() {
    return {
      errorMessage: '',
      errors: [],
      hasErrors: false,
      STATES: STATES,
      state: '',
      saveMessage: '',
      publishError: undefined,
    }
  },
  computed: {
    ...mapFields([
      'controls',
      'controlsLoadStatus',
      'currentQuestionnaire',
    ]),
  },
  watch: {
    // Watch change of loadStatus coming from the store, to know when the data is ready.
    controlsLoadStatus(newValue, oldValue) {
      const loadNewQuestionnaire = () => {
        console.debug('loadNewQuestionnaire')
        const newQuestionnaire = {
          control: this.controlId,
          description: QuestionnaireMetadataCreate.DESCRIPTION_DEFAULT,
          title: '',
          themes: [],
        }
        console.debug('currentQuestionnaire is new', newQuestionnaire)
        this.currentQuestionnaire = newQuestionnaire
        this.emitQuestionnaireUpdated()
        this.moveToState(STATES.START)
        return
      }

      const loadExistingQuestionnaire = () => {
        console.debug('loadExistingQuestionnaire')
        const currentQuestionnaire =
          this.findCurrentQuestionnaire(this.controls, this.questionnaireId)
        console.debug('currentQuestionnaire', currentQuestionnaire)
        if (!currentQuestionnaire) {
          const errorMessage = 'Le questionnaire ' + this.questionnaireId + ' n\'a pas été trouvé.'
          this.displayErrors(errorMessage)
          throw new Error('Questionnaire ' + this.questionnaireId + ' not found')
        }
        if (!currentQuestionnaire.is_draft) {
          const errorMessage = 'Le questionnaire ' + this.questionnaireId +
                ' n\'est pas un brouillon. Vous ne pouvez pas le modifier.'
          this.displayErrors(errorMessage)
          throw new Error(
            'Questionnaire ' + this.questionnaireId + ' is not a draft, you cannot edit it')
        }
        this.currentQuestionnaire = currentQuestionnaire
        this.emitQuestionnaireUpdated()
        this.moveToState(STATES.START)
      }

      if (newValue === loadStatuses.ERROR) {
        const errorMessage =
          'Erreur lors du chargement des données. Le questionnaire ne peut être affiché.'
        this.displayErrors(errorMessage)
        throw new Error('Store status is ERROR. Not loading questionnaire.')
      }
      if (newValue === loadStatuses.SUCCESS) {
        if (typeof this.questionnaireId === 'undefined') {
          loadNewQuestionnaire()
          return
        }
        loadExistingQuestionnaire()
      }
    },
  },
  components: {
    EmptyModal,
    PublishConfirmModal,
    QuestionnaireBodyCreate,
    QuestionnaireMetadataCreate,
    QuestionnairePreview,
    SwapEditorButton,
    Wizard,
  },
  mixins: [
    StickyBottomMixin,
  ],
  mounted() {
    this.stickyBottom_makeStickyBottom('bottom-bar', 140)

    console.debug('questionnaireId', this.questionnaireId)
    console.debug('controlId', this.controlId)
    if (this.controlId === undefined && this.questionnaireId === undefined) {
      throw Error('QuestionnaireCreate needs a controlId or a questionnaireId')
    }

    $('#publishConfirmModal').on('hidden.bs.modal', () => {
      this.publishError = undefined
    })
  },
  methods: {
    findCurrentQuestionnaire: function(controls, questionnaireId) {
      for (let i = 0; i < controls.length; i++) {
        const control = controls[i]
        const foundQuestionnaires =
          control.questionnaires.filter(questionnaire => questionnaire.id === questionnaireId)
        if (foundQuestionnaires.length > 0) {
          return foundQuestionnaires[0]
        }
      }
    },
    emitQuestionnaireUpdated: function() {
      this.$emit('questionnaire-updated', this.currentQuestionnaire)
    },
    moveToState: function(newState) {
      this.clearErrors()
      this.state = newState
    },
    next: function() {
      console.debug('Navigation "next" from', this.state)
      if (this.state === STATES.START) {
        if (!this.$refs.questionnaireMetadataCreate.validateForm()) {
          return
        }
        this.saveDraft().then(() => {
          // If there are no themes, add an empty theme and question, to prompt the user to add
          // more.
          if (this.currentQuestionnaire.themes.length === 0) {
            this.currentQuestionnaire.themes.push({ questions: [{}] })
          }
          this.moveToState(STATES.CREATING_BODY)
          return
        })
        return
      }
      if (this.state === STATES.CREATING_BODY) {
        if (!this.$refs.questionnaireBodyCreate.validateForm()) {
          return
        }
        this.saveDraft()
        this.moveToState(STATES.PREVIEW)
        return
      }
      console.error('Trying to go to "next", from state', this.state)
    },
    back: function(clickedStep) {
      console.debug('Navigation "back" from', this.state, 'going to step', clickedStep)
      if (this.state === STATES.CREATING_BODY) {
        if (!this.$refs.questionnaireBodyCreate.validateForm()) {
          return
        }
        this.saveDraft()
        this.moveToState(STATES.START)
        return
      }
      if (this.state === STATES.PREVIEW) {
        if (clickedStep === 1) {
          this.moveToState(STATES.START)
          return
        }
        if (clickedStep === 2) {
          this.moveToState(STATES.CREATING_BODY)
          return
        }
        // no step specified so, go to previous step by default
        this.moveToState(STATES.CREATING_BODY)
        return
      }
      console.error('Trying to go back from state', this.state, 'with clickedStep', clickedStep)
    },
    displayErrors: function(errorMessage, errors) {
      this.hasErrors = true
      this.errors = errors
      if (errors) {
        this.errorMessage = errorMessage + ' Erreurs : ' + JSON.stringify(errors)
      } else {
        this.errorMessage = errorMessage
      }
      console.error(errorMessage)
    },
    clearErrors() {
      this.hasErrors = false
      this.errors = []
      this.errorMessage = ''
    },
    clearSaveMessage() {
      this.saveMessage = ''
    },
    _doSave() {
      const cleanPreSave = () => {
        if (this.currentQuestionnaire.end_date) {
          this.currentQuestionnaire.end_date =
            moment(String(this.currentQuestionnaire.end_date)).format('YYYY-MM-DD')
        } else {
          // remove empty strings, it throws date format error.
          delete this.currentQuestionnaire.end_date
        }
      }
      const getCreateMethod = () => axios.post.bind(this, backend.questionnaire())
      const getUpdateMethod =
          (questionnaireId) => axios.put.bind(this, backend.questionnaire(questionnaireId))

      this.clearErrors()
      cleanPreSave()

      let saveMethod
      if (this.currentQuestionnaire.id !== undefined) {
        saveMethod = getUpdateMethod(this.currentQuestionnaire.id)
      } else {
        saveMethod = getCreateMethod()
      }
      return saveMethod(this.currentQuestionnaire)
    },
    validateCurrentForm() {
      if (this.state === STATES.PREVIEW) {
        return true
      }
      if (this.state === STATES.START) {
        return this.$refs.questionnaireMetadataCreate.validateForm()
      }
      if (this.state === STATES.CREATING_BODY) {
        return this.$refs.questionnaireBodyCreate.validateForm()
      }
    },
    saveDraftAndSwapEditor() {
      console.debug('save draft before editor swap')
      if (!this.validateCurrentForm()) {
        return
      }
      this.saveDraft()
        .then(savedQuestionnaire => {
          this.$emit('show-swap-editor-modal', savedQuestionnaire.id)
        })
    },
    validateFormAndSaveDraft() {
      if (!this.validateCurrentForm()) {
        return
      }
      this.saveDraft()
    },
    saveDraft() {
      this.currentQuestionnaire.is_draft = true
      return this._doSave()
        .then((response) => {
          console.log('Successful draft save.')
          this.currentQuestionnaire = response.data
          this.emitQuestionnaireUpdated()

          const timeString = moment(new Date()).format('HH:mm:ss')
          this.saveMessage = 'Votre dernière sauvegarde a eu lieu à ' + timeString + '.'
          return response.data
        })
        .catch((error) => {
          console.error('Error in draft save :', error)
          const errorToDisplay =
            (error.response && error.response.data) ? error.response.data : error
          this.displayErrors('Erreur lors de la sauvegarde du brouillon.', errorToDisplay)
        })
    },
    wait(timeMillis) {
      return new Promise((resolve) => {
        const id = setTimeout(() => {
          clearTimeout(id)
          resolve()
        }, timeMillis)
      })
    },
    showPublishConfirmModal: function () {
      $(this.$refs.publishConfirmModal.$el).modal('show')
    },
    publish() {
      $(this.$refs.savingModal.$el).modal('show')
      this.currentQuestionnaire.is_draft = false

      // Leave the "Saving..." modal for at least PUBLISH_TIME_MILLIS.
      // This is for the user to see the wait modal and be satisfied that the saving really
      // happened.
      return Promise.all([this.wait(PUBLISH_TIME_MILLIS), this._doSave()])
        .then(() => {
          console.debug('Done publishing questionnaire.')
          $(this.$refs.savingModal.$el).modal('hide')
          $(this.$refs.savedModal.$el).modal('show')
        })
        .catch(error => {
          console.error('Error publishing questionnaire : ', error)
          this.publishError = error
          $(this.$refs.savingModal.$el).modal('hide')
          this.showPublishConfirmModal()
        })
    },
    saveDraftAndGoHome(event) {
      if (!this.validateCurrentForm()) {
        return
      }
      // Display a "loading" spinner on clicked button, while the user is redirected, so that they
      // know their click has been registered.
      $(event.target).addClass('btn-loading')
      this.saveDraft()
        .then(() => {
          // Whether or not save succeeds, navigate to home
          this.goHome()
        })
    },
    goHome() {
      this.window.location.href = backend['control-detail'](this.currentQuestionnaire.control)
    },
    saveAndShowMoveThemesModal() {
      if (!this.validateCurrentForm()) {
        return
      }
      this.saveDraft()
        .then(() => {
          $(this.$refs.questionnaireBodyCreate.$refs.moveThemesModal.$el).modal('show')
        })
    },
  },
})
</script>

<style></style>

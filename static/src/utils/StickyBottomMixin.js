export default {
  methods: {
    stickyBottom_makeStickyBottom(elementId, bottomOffsetPx) {
      const stickySupport = this.stickyBottom_isPositionStickySupported()
      console.log('stickySupport', stickySupport)

      if (!stickySupport) {
        this.stickyBottom_makeStickyByHand(elementId, bottomOffsetPx)
      }
    },
    stickyBottom_isPositionStickySupported() {
      const prefix = ['', '-o-', '-webkit-', '-moz-', '-ms-']
      const test = document.head.style

      for (let i = 0; i < prefix.length; i += 1) {
        test.position = `${prefix[i]}sticky`
      }

      return test.position === 'sticky'
    },
    // Execute listenerFunc when document height changes.
    $_stickyBottom_listenToDocHeightChange(listenerFunc) {
      let docHeight = $(document).height()
      const pollPeriodMs = 300
      const pollFunc = () => {
        const newDocHeight = $(document).height()
        if (newDocHeight !== docHeight) {
          docHeight = newDocHeight
          listenerFunc(docHeight)
        }
      }
      setInterval(pollFunc, pollPeriodMs)
    },
    stickyBottom_makeStickyByHand(elementId, bottomOffsetPx) {
      const element = document.getElementById(elementId)
      const elementHeightPx = element.offsetHeight

      // Create a placeholder element of the same height as the fixed element.
      const placeholderElement = document.createElement('div')
      $(placeholderElement).css('min-height', elementHeightPx + 'px')
      element.parentNode.insertBefore(placeholderElement, element)

      // Position the element on top of the placeholder.
      const stickyMenu = $('#' + elementId)
      stickyMenu.css('position', 'absolute')
      stickyMenu.css('bottom', bottomOffsetPx + 'px')
      stickyMenu.css('z-index', 99)

      // Set the width. Needs to change if width of page changes (window resize of change in page)
      const setWidth = () => {
        const elementWidthPx = placeholderElement.offsetWidth
        stickyMenu.css('min-width', elementWidthPx + 'px')
      }
      setWidth()

      // Set the left offset. Needs to follow horizontal scroll.
      const setLeftOffset = () => {
        const leftOffset = placeholderElement.getBoundingClientRect().left
        stickyMenu.css('left', leftOffset + 'px')
      }
      setLeftOffset()

      // Depending on how far we have scrolled, position the element fixed or absolute.
      const positionElement = () => {
        const scrollDistance = $(document).scrollTop()
        const viewPortHeight = $(window).height()
        const stickyMenu = $('#' + elementId)
        if ((scrollDistance + viewPortHeight) <= ($(document).height() - bottomOffsetPx)) {
          stickyMenu.css('position', 'fixed')
          stickyMenu.css('bottom', '0')
        } else {
          stickyMenu.css('position', 'absolute')
          stickyMenu.css('bottom', bottomOffsetPx + 'px')
        }
        // Reset the width in case page width changed.
        setWidth()
        // Reset the left offset, in case there was horizontal scroll.
        setLeftOffset()
      }

      // Listen to scroll event, to reposition element on scroll
      $(document).scroll(positionElement)

      // Listen to doc height change, to reposition element on change
      this.$_stickyBottom_listenToDocHeightChange(positionElement)

      // Listen to window resize event, to reposition element on change
      $(window).resize(positionElement)
    },
  },
}

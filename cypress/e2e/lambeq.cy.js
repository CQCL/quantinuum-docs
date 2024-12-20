import { checkThatNavBarExists } from './utils.js'
  
  describe('E2E Tests', () => {
    it('can view / (landing page)', () => {
      cy.visit('/lambeq/')
      checkThatNavBarExists()
      cy.contains(/natural language processing on quantum computers/i)
      cy.contains(/pip install lambeq/i)
      cy.contains(/github/i)
      cy.contains(/discord/i)
      cy.contains(/getting started/i)
      cy.contains(/tutorials/i)
      cy.contains(/advanced/i)
    })
  
    it("examples is accessed from Navbar -> Lambeq", {
      retries: {
        // Nav dropdown is flaky at the moment.
        runMode: 5,
        openMode: 5,
      }
    },() => {  
      cy.visit('/lambeq/')
      cy.contains('button', 'λambeq').should('be.visible').click();
      cy.contains(/a python toolkit for quantum natural language processing/i).should("be.visible")
      cy.contains(/getting started/i).should("be.visible")
      cy.contains(/user guide/i).should("be.visible")
      cy.contains(/tutorials/i).should("be.visible")
      cy.contains(/code examples/i).should("be.visible")
      cy.contains(/api reference/i).click();
      cy.contains(/lambeq package/i)
    })
  
    it('inspect getting started', () => {
      cy.visit('//lambeq/intro.html')
      checkThatNavBarExists()
      cy.contains(/what is lambeq?/i)
    })
  
    it('inspect user guide', () => {
      cy.visit('/lambeq/pipeline.html')
      checkThatNavBarExists()
      cy.contains(/pipeline/i)
      cy.contains(/syntax tree for the sentence is obtained/i)
    })

    it('inspect tutorials', () => {
        cy.visit('/lambeq/tutorials/sentence-input.html')
        checkThatNavBarExists()
        cy.contains(/step 1. sentence input/i)
        cy.contains(/pre-processing and tokenisation/i)
        cy.contains(/syntax-based model: discocat/i)
    })

    it('inspect examples', () => {
        cy.visit('/lambeq/notebooks.html')
        checkThatNavBarExists()
        cy.contains(/tokenisation/i)
    })
  
   it.skip('can link to root docs page from lambeq guides page', () => {
      cy.visit('/lambeq/guides.html')
     cy.findByLabelText(/quantinuum documentation/i).click()
    cy.origin('https://docs.quantinuum.com', () => {
    cy.contains(/technical documentation/i)
   })
  })
  })
  